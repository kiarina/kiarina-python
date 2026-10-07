import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from kiarina.agi.chat_provider import TokenOverflowError
from kiarina.agi.chat_provider_impl.codex_app_server import (
    CodexAppServerChatProvider,
    CodexAppServerChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.codex_app_server._models.codex_app_server_session import (
    CodexAppServerSession,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk, HumanMessage, SystemMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import create_tool_info
from kiarina.utils.file import FileBlob

_FAKE_APP_SERVER = """
import json, sys

events = json.load(open(sys.argv[1]))
log = open(sys.argv[2], "w")

def send(message):
    sys.stdout.write(json.dumps(message) + "\\n")
    sys.stdout.flush()

for line in sys.stdin:
    message = json.loads(line)
    log.write(line)
    log.flush()

    if "id" not in message:
        continue

    if message["method"] == "thread/start":
        send({"id": message["id"], "result": {"thread": {"id": "thread_1"}}})
    elif message["method"] == "turn/start":
        send({"id": message["id"], "result": {"turn": {"id": "turn_1"}}})
        for event in events:
            if event == "exit":
                sys.exit(1)
            send(event)
    else:
        send({"id": message["id"], "result": {}})
"""

_USAGE = {
    "inputTokens": 100,
    "cachedInputTokens": 40,
    "outputTokens": 10,
    "reasoningOutputTokens": 3,
    "totalTokens": 110,
}


def _raw_item(item: dict[str, Any]) -> dict[str, Any]:
    return {"method": "rawResponseItem/completed", "params": {"item": item}}


def _tool_events() -> list[Any]:
    """The order in the lab capture: items, the end of the response, then the request."""
    return [
        _raw_item({"type": "message", "role": "user", "content": []}),
        _raw_item(
            {
                "type": "function_call",
                "call_id": "call_1",
                "name": "get_weather",
                "arguments": '{"city": "Nagoya"}',
            }
        ),
        {"method": "rawResponse/completed", "params": {"usage": _USAGE}},
        {
            "id": 0,
            "method": "item/tool/call",
            "params": {"tool": "get_weather", "callId": "call_1"},
        },
    ]


def _text_events() -> list[Any]:
    return [
        {"method": "item/agentMessage/delta", "params": {"delta": "Hi"}},
        _raw_item(
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Hi"}],
            }
        ),
        {"method": "rawResponse/completed", "params": {"usage": _USAGE}},
        {"method": "turn/completed", "params": {"turn": {"status": "completed"}}},
    ]


class _Recorder:
    def __init__(self) -> None:
        self.records: list[CostRecord] = []

    def add(self, record: CostRecord) -> None:
        self.records.append(record)


def _create_provider(
    tmp_path: Path, events: list[Any], **kwargs: Any
) -> CodexAppServerChatProvider:
    script = tmp_path / "fake_app_server.py"
    script.write_text(_FAKE_APP_SERVER)
    events_path = tmp_path / "events.json"
    events_path.write_text(json.dumps(events))

    provider = CodexAppServerChatProvider(CodexAppServerChatProviderSettings(**kwargs))
    provider.name = "codex_app_server"
    provider.create_session = lambda tmp: CodexAppServerSession(  # type: ignore[method-assign]
        [sys.executable, str(script), str(events_path), str(tmp_path / "log.jsonl")],
        env=dict(os.environ),
        cwd=str(tmp),
    )
    return provider


def _read_log(tmp_path: Path) -> dict[str, Any]:
    lines = [
        json.loads(line) for line in (tmp_path / "log.jsonl").read_text().splitlines()
    ]
    return {line["method"]: line.get("params") for line in lines}


async def _run(
    provider: CodexAppServerChatProvider, run_context: RunContext, **kwargs: Any
) -> list[AIMessageChunk | AIMessage]:
    kwargs.setdefault("cost_recorder", _Recorder())

    return [
        ai_message
        async for ai_message in provider.run(
            [SystemMessage.create("Be brief."), HumanMessage.create("Weather?")],
            run_context=run_context,
            **kwargs,
        )
    ]


# --------------------------------------------------
# Properties and media
# --------------------------------------------------


def test_codex_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("CODEX_HOME", raising=False)
    settings = CodexAppServerChatProviderSettings

    assert CodexAppServerChatProvider(settings()).codex_home == Path.home() / ".codex"

    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    assert CodexAppServerChatProvider(settings()).codex_home == tmp_path

    provider = CodexAppServerChatProvider(settings(codex_home="~/codex"))
    assert provider.codex_home == Path.home() / "codex"


def test_to_image_content(image_file_blob: FileBlob) -> None:
    provider = CodexAppServerChatProvider(CodexAppServerChatProviderSettings())
    content = provider.to_image_content(image_file_blob.mime_blob)

    assert content is not None
    assert content["type"] == "image"
    assert content["url"].startswith("data:image/png;base64,")
    assert provider.get_capabilities().can_include("human", "image")


def test_create_session(tmp_path: Path) -> None:
    (tmp_path / "models_cache.json").write_text(
        json.dumps({"models": [{"slug": "gpt-6.1-sol"}]})
    )
    provider = CodexAppServerChatProvider(
        CodexAppServerChatProviderSettings(
            codex_home=str(tmp_path),
            codex_bin="/bin/codex",
            config_overrides=['model_provider="mock"'],
        )
    )

    session = provider.create_session(tmp_path)

    args = session._args
    assert args[0] == "/bin/codex"
    assert args[-3:] == ["app-server", "--listen", "stdio://"]
    assert args[args.index('model_provider="mock"') - 1] == "--config"
    assert (tmp_path / "models.json").is_file()


# --------------------------------------------------
# Run
# --------------------------------------------------


@pytest.mark.parametrize("streaming", [False, True])
async def test_run_tool_call(
    tmp_path: Path, streaming: bool, run_context: RunContext
) -> None:
    provider = _create_provider(tmp_path, _tool_events(), reasoning_effort="medium")
    recorder = _Recorder()
    tool_info = create_tool_info(
        {"title": "get_weather", "description": "Get the weather.", "properties": {}}
    )

    ai_messages = await _run(
        provider,
        run_context,
        tool_infos=[tool_info],
        tool_choice="get_weather",
        streaming=streaming,
        cost_recorder=recorder,
    )

    ai_message = ai_messages[-1]
    assert isinstance(ai_message, AIMessage)
    assert [(tc.id, tc.name, tc.args) for tc in ai_message.tool_calls] == [
        ("call_1", "get_weather", {"city": "Nagoya"})
    ]

    if streaming:
        [chunk] = ai_messages[:-1]
        assert chunk.tool_call_chunks[0].index == 0  # type: ignore[union-attr]
        assert chunk.tool_call_chunks[0].args == '{"city": "Nagoya"}'  # type: ignore[union-attr]

    log = _read_log(tmp_path)
    assert log["initialize"]["capabilities"] == {"experimentalApi": True}
    assert log["thread/start"]["baseInstructions"].startswith("Be brief.\n\n")
    assert log["thread/start"]["experimentalRawEvents"] is True
    assert log["thread/start"]["dynamicTools"][0]["name"] == "get_weather"
    assert log["turn/start"]["threadId"] == "thread_1"
    assert log["turn/start"]["effort"] == "medium"
    assert log["turn/start"]["input"][0]["text"].endswith(
        "You must respond by calling the `get_weather` tool."
    )

    [record] = recorder.records
    assert record.microdollars == 0
    assert record.metadata == {
        "model_name": "gpt-6.1-sol",
        "input_tokens": 60,
        "cached_input_tokens": 40,
        "output_tokens": 10,
        "reasoning_output_tokens": 3,
    }


@pytest.mark.parametrize("streaming", [False, True])
async def test_run_text(
    tmp_path: Path, streaming: bool, run_context: RunContext
) -> None:
    provider = _create_provider(tmp_path, _text_events(), reasoning_effort=None)

    ai_messages = await _run(provider, run_context, streaming=streaming)

    assert ai_messages[-1].to_text() == "Hi"
    assert [m.to_text() for m in ai_messages[:-1]] == (["Hi"] if streaming else [])
    assert "effort" not in _read_log(tmp_path)["turn/start"]


@pytest.mark.parametrize(
    ("events", "error_type", "match"),
    [
        (
            [
                {"method": "error", "params": {"willRetry": True, "error": {}}},
                {
                    "method": "error",
                    "params": {
                        "willRetry": False,
                        "error": {
                            "message": "too long",
                            "codexErrorInfo": "contextWindowExceeded",
                        },
                    },
                },
            ],
            TokenOverflowError,
            "272000",
        ),
        (
            [{"method": "error", "params": {"error": {"message": "usage limit"}}}],
            RuntimeError,
            "usage limit",
        ),
        (
            [{"method": "turn/completed", "params": {"turn": {"error": None}}}],
            RuntimeError,
            "without a response",
        ),
        (["exit"], RuntimeError, "exited"),
    ],
)
async def test_run_errors(
    tmp_path: Path,
    events: list[Any],
    error_type: type[Exception],
    match: str,
    run_context: RunContext,
) -> None:
    provider = _create_provider(tmp_path, events)

    with pytest.raises(error_type, match=match):
        await _run(provider, run_context)
