from collections.abc import AsyncIterator
from typing import Any

import claude_agent_sdk
import pytest
from claude_agent_sdk import (
    AssistantMessage,
    ResultError,
    ResultMessage,
    StreamEvent,
    TextBlock,
    ToolUseBlock,
)

from kiarina.agi.chat_provider import MaxTokenError, SafetyError, TokenOverflowError
from kiarina.agi.chat_provider_impl.claude_agent_sdk import (
    ClaudeAgentSDKChatProvider,
    ClaudeAgentSDKChatProviderSettings,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import AIMessage, AIMessageChunk, HumanMessage, SystemMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo, create_tool_info
from kiarina.utils.file import FileBlob


def _create_provider(**kwargs: Any) -> ClaudeAgentSDKChatProvider:
    provider = ClaudeAgentSDKChatProvider(ClaudeAgentSDKChatProviderSettings(**kwargs))
    provider.name = "claude_agent_sdk"
    return provider


def _tool_info() -> ToolInfo:
    return create_tool_info(
        {
            "title": "get_weather",
            "description": "Get the weather.",
            "properties": {"city": {"type": "string"}},
        }
    )


def _result_message(**kwargs: Any) -> ResultMessage:
    fields: dict[str, Any] = {
        "subtype": "error_max_turns",
        "duration_ms": 1,
        "duration_api_ms": 1,
        "is_error": True,
        "num_turns": 1,
        "session_id": "s",
        "stop_reason": "tool_use",
        "total_cost_usd": 0.0123,
        "usage": {
            "input_tokens": 10,
            "cache_creation_input_tokens": 20,
            "cache_read_input_tokens": 30,
            "output_tokens": 5,
        },
    }
    return ResultMessage(**{**fields, **kwargs})


def _event(event: dict[str, Any]) -> StreamEvent:
    return StreamEvent(uuid="u", session_id="s", event=event)


def _tool_turn() -> list[Any]:
    """What Claude Code sends for a turn with a tool call, as in the lab capture."""
    return [
        _event(
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {
                    "type": "tool_use",
                    "id": "toolu_1",
                    "name": "mcp__app__get_weather",
                    "input": {},
                },
            }
        ),
        _event(
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": '{"city":"x"}'},
            }
        ),
        AssistantMessage(
            content=[
                ToolUseBlock(
                    id="toolu_1", name="mcp__app__get_weather", input={"city": "x"}
                )
            ],
            model="claude-sonnet-5-5",
        ),
        _event({"type": "message_stop"}),
        _result_message(),
    ]


def _text_turn(**result: Any) -> list[Any]:
    return [
        _event(
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": "Hi"},
            }
        ),
        AssistantMessage(content=[TextBlock(text="Hi")], model="claude-sonnet-5-5"),
        _result_message(
            **{"subtype": "success", "is_error": False, "stop_reason": "end_turn"}
            | result
        ),
    ]


class _FakeQuery:
    def __init__(self, messages: list[Any], *, error: Exception | None = None) -> None:
        self.messages = messages
        self.error = error
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, *, prompt: Any, options: Any) -> AsyncIterator[Any]:
        self.calls.append(
            {"prompt": [item async for item in prompt], "options": options}
        )

        for message in self.messages:
            yield message

        if self.error:
            raise self.error


class _Recorder:
    def __init__(self) -> None:
        self.records: list[CostRecord] = []

    def add(self, record: CostRecord) -> None:
        self.records.append(record)


async def _run(
    provider: ClaudeAgentSDKChatProvider,
    *,
    cost_recorder: CostRecorder,
    run_context: RunContext,
    **kwargs: Any,
) -> list[AIMessageChunk | AIMessage]:
    return [
        ai_message
        async for ai_message in provider.run(
            [SystemMessage.create("Be brief."), HumanMessage.create("Weather?")],
            cost_recorder=cost_recorder,
            run_context=run_context,
            **kwargs,
        )
    ]


# --------------------------------------------------
# Methods
# --------------------------------------------------


def test_get_capabilities() -> None:
    capabilities = _create_provider(token_count_limit=1000).get_capabilities()

    assert capabilities.token_count_limit == 1000
    assert capabilities.can_include("human", "pdf")


def test_media_contents(image_file_blob: FileBlob, pdf_file_blob: FileBlob) -> None:
    provider = _create_provider()

    assert provider.to_image_content(image_file_blob.mime_blob)["type"] == "image"  # type: ignore[index]
    assert (
        provider.to_pdf_content(pdf_file_blob.mime_blob, display_name="a.pdf")["type"]  # type: ignore[index]
        == "document"
    )


def test_create_options(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-live")
    provider = _create_provider(effort="high", env={"FOO": "1"})

    options = provider.create_options(
        system_prompt="S", tool_infos=[_tool_info()], streaming=True, cwd="/tmp"
    )

    assert options.max_turns == 1
    assert options.tools == []
    assert options.setting_sources == []
    assert options.strict_mcp_config
    assert options.allowed_tools == ["mcp__app__get_weather"]
    assert list(options.mcp_servers) == ["app"]  # type: ignore[arg-type]
    assert options.effort == "high"
    assert options.include_partial_messages
    assert options.env["ANTHROPIC_API_KEY"] == ""
    assert options.env["FOO"] == "1"
    assert options.extra_args["no-session-persistence"] is None


def test_create_options_without_tools() -> None:
    options = _create_provider().create_options(
        system_prompt="S", tool_infos=[], streaming=False, cwd="/tmp"
    )

    assert options.mcp_servers == {}
    assert options.allowed_tools == []
    assert not options.include_partial_messages


@pytest.mark.parametrize("streaming", [False, True])
async def test_run_tool_call(
    monkeypatch: pytest.MonkeyPatch, streaming: bool, run_context: RunContext
) -> None:
    fake = _FakeQuery(_tool_turn(), error=ResultError("Reached maximum turns"))
    monkeypatch.setattr(claude_agent_sdk, "query", fake)
    recorder = _Recorder()

    ai_messages = await _run(
        _create_provider(),
        tool_infos=[_tool_info()],
        tool_choice="any",
        streaming=streaming,
        cost_recorder=recorder,  # type: ignore[arg-type]
        run_context=run_context,
    )

    ai_message = ai_messages[-1]
    assert isinstance(ai_message, AIMessage)
    assert [(tc.id, tc.name, tc.args) for tc in ai_message.tool_calls] == [
        ("toolu_1", "get_weather", {"city": "x"})
    ]

    if streaming:
        chunks = ai_messages[:-1]
        assert chunks[0].tool_call_chunks[0].name == "get_weather"  # type: ignore[union-attr]
        assert chunks[1].tool_call_chunks[0].args == '{"city":"x"}'  # type: ignore[union-attr]
    else:
        assert len(ai_messages) == 1

    [user_message] = fake.calls[0]["prompt"]
    first, last = user_message["message"]["content"]
    assert first == {
        "type": "text",
        "text": "<messages>\n<human_message>\nWeather?\n</human_message>",
        "cache_control": {"type": "ephemeral", "ttl": "1h"},
    }
    assert last["text"].startswith("</messages>\n\nRespond to the last message")
    assert last["text"].endswith(
        "You must respond by calling one of the provided tools."
    )
    assert fake.calls[0]["options"].system_prompt.startswith("Be brief.\n\n")

    [record] = recorder.records
    assert record.microdollars == 0
    assert record.metadata == {
        "model_name": "claude-sonnet-5-5",
        "input_tokens": 10,
        "cache_write_tokens": 20,
        "cached_input_tokens": 30,
        "output_tokens": 5,
        "api_cost_microdollars": 12_300,
    }


@pytest.mark.parametrize("streaming", [False, True])
async def test_run_text(
    monkeypatch: pytest.MonkeyPatch, streaming: bool, run_context: RunContext
) -> None:
    monkeypatch.setattr(claude_agent_sdk, "query", _FakeQuery(_text_turn()))

    ai_messages = await _run(
        _create_provider(),
        streaming=streaming,
        cost_recorder=_Recorder(),  # type: ignore[arg-type]
        run_context=run_context,
    )

    assert ai_messages[-1].to_text() == "Hi"
    assert len(ai_messages) == (2 if streaming else 1)


async def test_run_parallel_tool_calls_disabled(
    monkeypatch: pytest.MonkeyPatch, run_context: RunContext
) -> None:
    turn = _tool_turn()
    turn.insert(
        3,
        AssistantMessage(
            content=[
                ToolUseBlock(id="toolu_2", name="mcp__app__get_weather", input={})
            ],
            model="claude-sonnet-5-5",
        ),
    )
    monkeypatch.setattr(claude_agent_sdk, "query", _FakeQuery(turn))

    ai_messages = await _run(
        _create_provider(),
        tool_infos=[_tool_info()],
        parallel_tool_calls=False,
        cost_recorder=_Recorder(),  # type: ignore[arg-type]
        run_context=run_context,
    )

    assert [tc.id for tc in ai_messages[-1].tool_calls] == ["toolu_1"]


@pytest.mark.parametrize(
    ("stop_reason", "error_type"),
    [
        ("refusal", SafetyError),
        ("max_tokens", MaxTokenError),
        ("model_context_window_exceeded", MaxTokenError),
    ],
)
async def test_run_stop_reason_errors(
    monkeypatch: pytest.MonkeyPatch,
    stop_reason: str,
    error_type: type[Exception],
    run_context: RunContext,
) -> None:
    monkeypatch.setattr(
        claude_agent_sdk, "query", _FakeQuery(_text_turn(stop_reason=stop_reason))
    )

    with pytest.raises(error_type):
        await _run(
            _create_provider(),
            cost_recorder=_Recorder(),  # type: ignore[arg-type]
            run_context=run_context,
        )


async def test_run_token_overflow(
    monkeypatch: pytest.MonkeyPatch, run_context: RunContext
) -> None:
    result = _result_message(
        subtype="success", result="Prompt is too long: 250000 tokens > 200000 maximum"
    )
    monkeypatch.setattr(
        claude_agent_sdk,
        "query",
        _FakeQuery([result], error=ResultError("Prompt is too long")),
    )

    with pytest.raises(TokenOverflowError) as exc_info:
        await _run(
            _create_provider(),
            cost_recorder=_Recorder(),  # type: ignore[arg-type]
            run_context=run_context,
        )

    assert exc_info.value.token_count == 250_000


async def test_run_errors(
    monkeypatch: pytest.MonkeyPatch, run_context: RunContext
) -> None:
    monkeypatch.setattr(
        claude_agent_sdk,
        "query",
        _FakeQuery(
            [_result_message(subtype="error_during_execution", result="Not logged in")],
            error=ResultError("Not logged in"),
        ),
    )

    with pytest.raises(RuntimeError, match="Not logged in"):
        await _run(
            _create_provider(),
            cost_recorder=_Recorder(),  # type: ignore[arg-type]
            run_context=run_context,
        )

    monkeypatch.setattr(
        claude_agent_sdk, "query", _FakeQuery([], error=ResultError("crashed"))
    )

    with pytest.raises(ResultError):
        await _run(
            _create_provider(),
            cost_recorder=_Recorder(),  # type: ignore[arg-type]
            run_context=run_context,
        )

    monkeypatch.setattr(claude_agent_sdk, "query", _FakeQuery([]))

    with pytest.raises(RuntimeError, match="without a result"):
        await _run(
            _create_provider(),
            cost_recorder=_Recorder(),  # type: ignore[arg-type]
            run_context=run_context,
        )
