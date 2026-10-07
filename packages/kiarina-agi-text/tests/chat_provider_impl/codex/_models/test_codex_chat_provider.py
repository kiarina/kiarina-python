import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from kiarina.agi.chat_provider import ChatProviderState, TokenOverflowError
from kiarina.agi.chat_provider_impl.codex import (
    CodexChatProvider,
    CodexChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.codex._instances.live_thread_pool import (
    live_thread_pool,
)
from kiarina.agi.chat_provider_impl.codex._models.codex_app_server_session import (
    CodexAppServerSession,
)
from kiarina.agi.chat_provider_impl.codex._models.codex_chat_provider import (
    _to_tool_reply,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import (
    AIMessage,
    AIMessageChunk,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import create_tool_info
from kiarina.utils.file import FileBlob

_FAKE_APP_SERVER = """
import json, sys

phases = json.load(open(sys.argv[1]))
log = open(sys.argv[2], "a")
turns = 0

def send(message):
    sys.stdout.write(json.dumps(message) + "\\n")
    sys.stdout.flush()

def next_phase():
    for event in phases.pop(0) if phases else []:
        if event == "exit":
            sys.exit(1)
        send(event)

for line in sys.stdin:
    message = json.loads(line)
    log.write(line)
    log.flush()

    if "method" not in message:
        next_phase()  # a reply to a tool call request
    elif "id" not in message:
        continue
    elif message["method"] == "thread/start":
        send({"id": message["id"], "result": {"thread": {"id": "thread_1"}}})
    elif message["method"] == "turn/start":
        turns += 1
        send({"id": message["id"], "result": {"turn": {"id": f"turn_{turns}"}}})
        next_phase()
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
        {
            "method": "rawResponseItem/completed",
            "params": {
                "turnId": "turn_0",
                "item": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Old"}],
                },
            },
        },
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
    tmp_path: Path,
    events: list[Any] | None = None,
    *,
    phases: list[list[Any]] | None = None,
    **kwargs: Any,
) -> CodexChatProvider:
    """A provider whose app-server sends a phase on each turn start and reply."""
    script = tmp_path / "fake_app_server.py"
    script.write_text(_FAKE_APP_SERVER)
    events_path = tmp_path / "events.json"
    events_path.write_text(json.dumps(phases if phases is not None else [events]))

    provider = CodexChatProvider(CodexChatProviderSettings(**kwargs))
    provider.name = "codex"
    provider.create_session = lambda tmp: CodexAppServerSession(  # type: ignore[method-assign]
        [sys.executable, str(script), str(events_path), str(tmp_path / "log.jsonl")],
        env=dict(os.environ),
        cwd=str(tmp),
    )
    return provider


def _read_lines(tmp_path: Path) -> list[dict[str, Any]]:
    log = (tmp_path / "log.jsonl").read_text().splitlines()
    return [json.loads(line) for line in log]


def _read_log(tmp_path: Path) -> dict[str, Any]:
    return {
        line["method"]: line.get("params")
        for line in _read_lines(tmp_path)
        if "method" in line
    }


async def _run(
    provider: CodexChatProvider, run_context: RunContext, **kwargs: Any
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
    settings = CodexChatProviderSettings

    assert CodexChatProvider(settings()).codex_home == Path.home() / ".codex"

    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    assert CodexChatProvider(settings()).codex_home == tmp_path

    provider = CodexChatProvider(settings(codex_home="~/codex"))
    assert provider.codex_home == Path.home() / "codex"


def test_to_image_content(image_file_blob: FileBlob) -> None:
    provider = CodexChatProvider(CodexChatProviderSettings())
    content = provider.to_image_content(image_file_blob.mime_blob)

    assert content is not None
    assert content["type"] == "input_image"
    assert content["image_url"].startswith("data:image/png;base64,")
    assert provider.get_capabilities().can_include("human", "image")


def test_create_session(tmp_path: Path) -> None:
    (tmp_path / "models_cache.json").write_text(
        json.dumps({"models": [{"slug": "gpt-6.1-sol"}]})
    )
    provider = CodexChatProvider(
        CodexChatProviderSettings(
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
    assert log["thread/start"]["baseInstructions"] == "Be brief."
    assert log["thread/start"]["experimentalRawEvents"] is True
    assert log["thread/start"]["dynamicTools"][0]["name"] == "get_weather"
    assert log["thread/inject_items"]["threadId"] == "thread_1"
    assert [i["role"] for i in log["thread/inject_items"]["items"]] == [
        "user",
        "developer",
    ]
    assert log["turn/start"] == {
        "threadId": "thread_1",
        "input": [],
        "effort": "medium",
    }

    [record] = recorder.records
    assert record.microdollars == 0
    assert record.metadata == {
        "model_name": "gpt-6.1-sol",
        "input_tokens": 60,
        "cached_input_tokens": 40,
        "cache_write_tokens": 0,
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
    log = _read_log(tmp_path)
    assert "effort" not in log["turn/start"]
    assert log["thread/start"]["baseInstructions"] == "Be brief."


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


# --------------------------------------------------
# Thread reuse
# --------------------------------------------------


def _turn_event(method: str, turn_id: str, **params: Any) -> dict[str, Any]:
    return {"method": method, "params": {"turnId": turn_id, **params}}


def _reuse_phases() -> list[list[Any]]:
    """A tool call, then its result's answer, then a second turn."""
    return [
        [
            _turn_event(
                "rawResponseItem/completed",
                "turn_1",
                item={
                    "type": "function_call",
                    "call_id": "call_1",
                    "name": "get_weather",
                    "arguments": "{}",
                },
            ),
            {
                "id": 7,
                "method": "item/tool/call",
                "params": {"turnId": "turn_1", "callId": "call_1"},
            },
            _turn_event("rawResponse/completed", "turn_1", usage=_USAGE),
        ],
        [
            _turn_event("item/agentMessage/delta", "turn_1", delta="Sunny"),
            _turn_event(
                "rawResponseItem/completed",
                "turn_1",
                item={
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Sunny"}],
                },
            ),
            _turn_event("rawResponse/completed", "turn_1", usage=_USAGE),
            {"method": "turn/completed", "params": {"turn": {"id": "turn_1"}}},
        ],
        [
            _turn_event(
                "rawResponseItem/completed",
                "turn_2",
                item={
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Bye"}],
                },
            ),
            _turn_event("rawResponse/completed", "turn_2", usage=_USAGE),
        ],
    ]


async def _run_messages(
    provider: CodexChatProvider,
    messages: list[Any],
    run_context: RunContext,
    **kwargs: Any,
) -> AIMessage:
    tool_info = create_tool_info(
        {"title": "get_weather", "description": "Get the weather.", "properties": {}}
    )
    ai_messages = [
        m
        async for m in provider.run(
            messages,
            tool_infos=[tool_info],
            cost_recorder=_Recorder(),  # type: ignore[arg-type]
            run_context=run_context,
            **kwargs,
        )
    ]
    ai_message = ai_messages[-1]
    assert isinstance(ai_message, AIMessage)
    return ai_message


@pytest.mark.parametrize("streaming", [False, True])
async def test_thread_reuse(
    tmp_path: Path, streaming: bool, run_context: RunContext
) -> None:
    provider = _create_provider(tmp_path, phases=_reuse_phases())
    messages: list[Any] = [
        SystemMessage.create("Be brief."),
        HumanMessage.create("Weather?"),
    ]

    first = await _run_messages(provider, messages, run_context, streaming=streaming)
    state = ChatProviderState.from_message(first, "codex")
    assert state is not None
    assert state.data == {"thread_id": "thread_1"}
    assert len(live_thread_pool) == 1

    # The tool result answers the held request, and the same turn goes on.
    messages += [
        first,
        ToolMessage.create("sunny", tool_name="get_weather", tool_call_id="call_1"),
    ]
    second = await _run_messages(provider, messages, run_context, streaming=streaming)
    assert second.to_text() == "Sunny"
    assert ChatProviderState.from_message(second, "codex") is not None

    # A new message after the completed turn starts a new turn on the thread.
    messages += [second, HumanMessage.create("Thanks")]
    third = await _run_messages(provider, messages, run_context, streaming=streaming)
    assert third.to_text() == "Bye"
    assert len(live_thread_pool) == 1

    lines = _read_lines(tmp_path)
    methods = [line.get("method") for line in lines]
    assert methods.count("thread/start") == 1
    assert methods.count("turn/start") == 2
    assert {
        "id": 7,
        "result": {
            "contentItems": [{"type": "inputText", "text": "sunny"}],
            "success": True,
        },
    } in lines

    injects = [
        line["params"] for line in lines if line.get("method") == "thread/inject_items"
    ]
    assert len(injects) == 2
    assert injects[1]["items"] == [
        {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Thanks"}],
        }
    ]


async def test_thread_reuse_after_edit(tmp_path: Path, run_context: RunContext) -> None:
    provider = _create_provider(tmp_path, phases=_reuse_phases())
    first = await _run_messages(
        provider, [HumanMessage.create("Weather?")], run_context
    )

    # An edited history no longer matches the hash, so a new thread starts.
    second = await _run_messages(
        provider,
        [
            HumanMessage.create("Weather in Tokyo?"),
            first,
            ToolMessage.create("sunny", tool_name="get_weather", tool_call_id="call_1"),
        ],
        run_context,
    )

    assert second.tool_calls[0].id == "call_1"
    methods = [line.get("method") for line in _read_lines(tmp_path)]
    assert methods.count("thread/start") == 2
    assert len(live_thread_pool) == 1


async def test_thread_reuse_unexpected_tail(
    tmp_path: Path, run_context: RunContext
) -> None:
    provider = _create_provider(tmp_path, phases=_reuse_phases())
    messages: list[Any] = [HumanMessage.create("Weather?")]
    first = await _run_messages(provider, messages, run_context)

    # A paused turn takes only its tool results.
    await _run_messages(
        provider,
        [
            *messages,
            first,
            ToolMessage.create("sunny", tool_name="get_weather", tool_call_id="call_1"),
            HumanMessage.create("And tomorrow?"),
        ],
        run_context,
    )

    methods = [line.get("method") for line in _read_lines(tmp_path)]
    assert methods.count("thread/start") == 2


async def test_thread_reuse_after_failure(
    tmp_path: Path, run_context: RunContext
) -> None:
    provider = _create_provider(tmp_path, phases=_reuse_phases())
    messages: list[Any] = [HumanMessage.create("Weather?")]
    first = await _run_messages(provider, messages, run_context)

    live = live_thread_pool.take("thread_1")
    assert live is not None
    live.session.kill()
    live_thread_pool.put(live, idle_timeout=60, max_count=4)

    # The dead thread fails before anything is yielded, so a new one starts.
    second = await _run_messages(
        provider,
        [
            *messages,
            first,
            ToolMessage.create("sunny", tool_name="get_weather", tool_call_id="call_1"),
        ],
        run_context,
    )

    assert second.tool_calls[0].id == "call_1"
    methods = [line.get("method") for line in _read_lines(tmp_path)]
    assert methods.count("thread/start") == 2


@pytest.mark.parametrize(
    "kwargs",
    [{"thread_reuse": False}, {"tool_choice": "get_weather"}],
)
async def test_no_thread_reuse(
    tmp_path: Path, kwargs: dict[str, Any], run_context: RunContext
) -> None:
    settings = {k: v for k, v in kwargs.items() if k == "thread_reuse"}
    run_kwargs = {k: v for k, v in kwargs.items() if k != "thread_reuse"}
    provider = _create_provider(tmp_path, phases=_reuse_phases(), **settings)

    first = await _run_messages(
        provider, [HumanMessage.create("Weather?")], run_context, **run_kwargs
    )

    assert ChatProviderState.from_message(first, "codex") is None
    assert len(live_thread_pool) == 0


def test_to_tool_reply() -> None:
    assert _to_tool_reply(
        [
            {"type": "input_text", "text": "map"},
            {"type": "input_image", "image_url": "data:image/png;base64,x"},
            {"type": "unknown"},
        ]
    ) == {
        "contentItems": [
            {"type": "inputText", "text": "map"},
            {"type": "inputImage", "imageUrl": "data:image/png;base64,x"},
        ],
        "success": True,
    }
