from collections.abc import Callable
from typing import Any

import pytest
from anthropic.types import (
    Message as AnthropicMessage,
    RawContentBlockDeltaEvent,
    RawContentBlockStartEvent,
    RawMessageStartEvent,
)
from pydantic import BaseModel

from kiarina.agi.chat_provider import (
    ChatProviderContext,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.chat_provider_impl.anthropic import (
    AnthropicChatProvider,
    AnthropicChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.anthropic._schemas.anthropic_usage import (
    AnthropicUsage,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.file_info import ImageFileInfo, PDFFileInfo
from kiarina.agi.message import (
    AIMessage,
    AIMessageChunk,
    HumanMessage,
    Message,
    SystemMessage,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo, create_tool_info
from kiarina.utils.file import FileBlob


def _create_provider(**kwargs: Any) -> AnthropicChatProvider:
    provider = AnthropicChatProvider(AnthropicChatProviderSettings(**kwargs))
    provider.name = "anthropic"
    return provider


async def _run(
    provider: AnthropicChatProvider,
    messages: list[Message],
    *,
    cost_recorder: CostRecorder,
    run_context: RunContext,
    **kwargs: Any,
) -> list[AIMessageChunk | AIMessage]:
    return [
        ai_message
        async for ai_message in provider.run(
            messages, cost_recorder=cost_recorder, run_context=run_context, **kwargs
        )
    ]


# --------------------------------------------------
# Properties
# --------------------------------------------------


def test_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    provider = _create_provider(model_name="claude-test", context_1m_enabled=True)

    assert str(provider) == "AnthropicChatProvider(claude-test, context_1m)"
    assert provider.client is provider.client
    assert provider.token_count_model_name == "claude-test"


def test_get_capabilities() -> None:
    capabilities = _create_provider(
        token_count_limit=2048, input_enabled={"image": True}
    ).get_capabilities()

    assert capabilities.token_count_limit == 2048
    assert capabilities.can_include("human", "image")
    assert not capabilities.can_include("human", "pdf")


def test_media_contents(image_file_blob: FileBlob, pdf_file_blob: FileBlob) -> None:
    provider = _create_provider()
    image = provider.to_image_content(image_file_blob.mime_blob)
    pdf = provider.to_pdf_content(pdf_file_blob.mime_blob, display_name="a.pdf")

    assert image is not None and image["source"]["media_type"] == "image/png"
    assert pdf is not None and pdf["type"] == "document"


# --------------------------------------------------
# Request
# --------------------------------------------------


@pytest.fixture
def ctx(run_context: RunContext) -> ChatProviderContext:
    return ChatProviderContext.create(
        messages=[HumanMessage.create("Hello")], run_context=run_context
    )


async def test_create_request(ctx: ChatProviderContext) -> None:
    request = await _create_provider(model_name="claude-test").create_request(ctx)

    assert request == {
        "model": "claude-test",
        "messages": [{"role": "user", "content": [{"type": "text", "text": "Hello"}]}],
        "max_tokens": 64_000,
        "extra_body": {"temperature": 0.0},
    }


async def test_create_request_with_options(
    ctx: ChatProviderContext, tool_infos: list[ToolInfo]
) -> None:
    provider = _create_provider(temperature=None, context_1m_enabled=True)
    ctx.messages.insert(0, SystemMessage.create(""))
    ctx.tool_infos = tool_infos
    ctx.tool_choice = "any"

    request = await provider.create_request(ctx)

    assert request["system"] == "<no message>"
    assert "extra_body" not in request
    assert request["extra_headers"] == {"anthropic-beta": "context-1m-2025-08-07"}
    assert request["tools"][0]["name"] == "get_weather"
    assert request["tool_choice"] == {"type": "any", "disable_parallel_tool_use": True}


async def test_create_request_forced_tool_choice_unsupported(
    ctx: ChatProviderContext, tool_infos: list[ToolInfo]
) -> None:
    provider = _create_provider(model_name="claude-sonnet-5-5")
    ctx.tool_infos = tool_infos
    ctx.tool_choice = "any"

    request = await provider.create_request(ctx)

    assert request["tool_choice"]["type"] == "auto"
    assert request["messages"][-1]["content"][-1] == {
        "type": "text",
        "text": "You must respond by calling one of the provided tools.",
    }


# --------------------------------------------------
# Invocation (fake client)
# --------------------------------------------------


class _FakeStream:
    def __init__(self, events: list[Any], message: AnthropicMessage) -> None:
        self.events = events
        self.message = message

    async def __aenter__(self) -> "_FakeStream":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass

    def __aiter__(self) -> "_FakeStream":
        return self

    async def __anext__(self) -> Any:
        if not self.events:
            raise StopAsyncIteration
        return self.events.pop(0)

    async def get_final_message(self) -> AnthropicMessage:
        return self.message


class _FakeMessages:
    def __init__(
        self,
        message: AnthropicMessage,
        events: list[Any],
        error: Exception | None,
        input_tokens: int | Exception,
    ) -> None:
        self.message = message
        self.events = events
        self.error = error
        self.input_tokens = input_tokens
        self.count_kwargs: dict[str, Any] = {}

    async def create(self, **kwargs: Any) -> AnthropicMessage:
        if self.error:
            raise self.error
        return self.message

    def stream(self, **kwargs: Any) -> _FakeStream:
        if self.error:
            raise self.error
        return _FakeStream(list(self.events), self.message)

    async def count_tokens(self, **kwargs: Any) -> Any:
        self.count_kwargs = kwargs

        if isinstance(self.input_tokens, Exception):
            raise self.input_tokens

        return type("Count", (), {"input_tokens": self.input_tokens})()


class _FakeClient:
    def __init__(
        self,
        message: AnthropicMessage,
        events: list[Any] | None = None,
        error: Exception | None = None,
        input_tokens: int | Exception = 10,
    ) -> None:
        self.messages = _FakeMessages(message, events or [], error, input_tokens)

    def with_options(self, **kwargs: Any) -> "_FakeClient":
        return self


@pytest.fixture
def fake_provider() -> AnthropicChatProvider:
    return _create_provider(token_count_limit=100)


def _stream_events() -> list[Any]:
    return [
        RawMessageStartEvent.model_validate(
            {
                "type": "message_start",
                "message": {
                    "id": "msg_1",
                    "type": "message",
                    "role": "assistant",
                    "model": "claude-test",
                    "content": [],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {"input_tokens": 1, "output_tokens": 1},
                },
            }
        ),
        RawContentBlockDeltaEvent.model_validate(
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": "Hi"},
            }
        ),
        RawContentBlockStartEvent.model_validate(
            {
                "type": "content_block_start",
                "index": 1,
                "content_block": {
                    "type": "tool_use",
                    "id": "toolu_1",
                    "name": "f",
                    "input": {},
                },
            }
        ),
        RawContentBlockDeltaEvent.model_validate(
            {
                "type": "content_block_delta",
                "index": 1,
                "delta": {"type": "input_json_delta", "partial_json": "{}"},
            }
        ),
    ]


@pytest.mark.parametrize("streaming", [False, True])
async def test_run(
    fake_provider: AnthropicChatProvider,
    make_message: Callable[..., AnthropicMessage],
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    client = _FakeClient(
        make_message([{"type": "text", "text": "Hi"}]), events=_stream_events()
    )
    fake_provider._client = client

    ai_messages = await _run(
        fake_provider,
        [HumanMessage.create("Hello")],
        streaming=streaming,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert ai_messages[-1].type == "ai"
    assert ai_messages[-1].to_text() == "Hi"
    assert client.messages.count_kwargs["model"] == "claude-haiku-4-5"

    if streaming:
        assert [m.to_text() for m in ai_messages[:3]] == ["Hi", "", ""]
        assert ai_messages[1].tool_call_chunks[0].name == "f"  # type: ignore[union-attr]
        assert ai_messages[2].tool_call_chunks[0].args == "{}"  # type: ignore[union-attr]


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize(
    ("stop_reason", "error_type"),
    [
        ("refusal", SafetyError),
        ("max_tokens", MaxTokenError),
        ("model_context_window_exceeded", MaxTokenError),
    ],
)
async def test_run_stop_reason_errors(
    fake_provider: AnthropicChatProvider,
    make_message: Callable[..., AnthropicMessage],
    streaming: bool,
    stop_reason: str,
    error_type: type[Exception],
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    fake_provider._client = _FakeClient(make_message(stop_reason=stop_reason))

    with pytest.raises(error_type):
        await _run(
            fake_provider,
            [HumanMessage.create("Hello")],
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize(
    ("message", "token_count"),
    [
        ("prompt is too long: 1200 tokens > 1000 maximum", 1200),
        ("input length and `max_tokens` exceed context limit: 900 + 200 > 1000", 900),
        ("Token overflow error: 1300 tokens", 1300),
        ("Something else", None),
    ],
)
async def test_run_request_errors(
    fake_provider: AnthropicChatProvider,
    make_message: Callable[..., AnthropicMessage],
    streaming: bool,
    message: str,
    token_count: int | None,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    fake_provider._client = _FakeClient(make_message(), error=RuntimeError(message))

    with pytest.raises((TokenOverflowError, RuntimeError)) as exc_info:
        await _run(
            fake_provider,
            [HumanMessage.create("Hello")],
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    if token_count is None:
        assert type(exc_info.value) is RuntimeError
    else:
        assert isinstance(exc_info.value, TokenOverflowError)
        assert exc_info.value.token_count == token_count


async def test_check_token_overflow(
    fake_provider: AnthropicChatProvider,
    make_message: Callable[..., AnthropicMessage],
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    fake_provider._client = _FakeClient(make_message(), input_tokens=101)

    with pytest.raises(TokenOverflowError) as exc_info:
        await _run(
            fake_provider,
            [HumanMessage.create("Hello")],
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    assert exc_info.value.token_count == 101


async def test_check_token_overflow_ignores_count_errors(
    fake_provider: AnthropicChatProvider,
    make_message: Callable[..., AnthropicMessage],
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    fake_provider._client = _FakeClient(
        make_message([{"type": "text", "text": "Hi"}]),
        input_tokens=RuntimeError("429"),
    )

    ai_messages = await _run(
        fake_provider,
        [HumanMessage.create("Hello")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert ai_messages[-1].to_text() == "Hi"


# --------------------------------------------------
# Cost
# --------------------------------------------------


@pytest.mark.parametrize(
    ("context_1m_enabled", "input_tokens", "expected_microdollars"),
    [
        (False, 1_000, 43_050),
        (True, 199_999, 640_047),
        (True, 200_000, 1_265_100),
    ],
)
def test_get_cost_record(
    context_1m_enabled: bool, input_tokens: int, expected_microdollars: int
) -> None:
    provider = _create_provider(context_1m_enabled=context_1m_enabled)

    cost_record = provider._get_cost_record(
        AnthropicUsage(
            input_tokens=input_tokens,
            cache_write_5m_tokens=1_000,
            cache_write_1h_tokens=1_000,
            cached_input_tokens=1_000,
            output_tokens=2_000,
        )
    )

    assert cost_record.microdollars == expected_microdollars
    assert cost_record.metadata == {
        "model_name": "claude-haiku-4-5",
        "input_tokens": input_tokens,
        "cache_write_5m_tokens": 1_000,
        "cache_write_1h_tokens": 1_000,
        "cached_input_tokens": 1_000,
        "output_tokens": 2_000,
    }


# --------------------------------------------------
# Use Cases (Anthropic API)
# --------------------------------------------------


@pytest.fixture
def provider(load_settings: None) -> AnthropicChatProvider:
    return _create_provider(
        model_name="claude-haiku-4-5-20251001",
        max_output_tokens=2_000,
        input_enabled={"image": True, "pdf": True},
        output_enabled={"image": True},
    )


@pytest.mark.costly
@pytest.mark.parametrize("streaming", [False, True])
async def test_hello(
    provider: AnthropicChatProvider,
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    ai_messages = await _run(
        provider,
        [HumanMessage.create("Hello")],
        streaming=streaming,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print(ai_messages[-1].to_text())

    assert ai_messages[-1].type == "ai"
    assert ai_messages[-1].to_text()


@pytest.mark.costly
async def test_count_tokens(
    provider: AnthropicChatProvider,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider.settings.token_count_limit = 1

    with pytest.raises(TokenOverflowError) as exc_info:
        await _run(
            provider,
            [HumanMessage.create("Hello")],
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    assert exc_info.value.token_count > 1


@pytest.mark.costly
async def test_cost_record_with_cache(
    provider: AnthropicChatProvider,
    large_text_file_blob: FileBlob,
    run_context: RunContext,
) -> None:
    from kiarina.agi.content import Content

    ctx = ChatProviderContext.create(
        messages=[
            HumanMessage(
                contents=[
                    Content(
                        text=large_text_file_blob.raw_text,
                        cache_control={"type": "ephemeral"},
                    )
                ]
            ),
            HumanMessage.create("Hello, how are you?"),
        ],
        run_context=run_context,
    )
    usages: list[AnthropicUsage | None] = []

    for _ in range(2):
        message = await provider.client.messages.create(
            **await provider.create_request(ctx)
        )
        from kiarina.agi.chat_provider_impl.anthropic._operations.from_anthropic_message import (
            from_anthropic_message,
        )

        result = from_anthropic_message(message, cache_ttl="5m")
        usages.append(result.usage)
        ctx.messages += [result.ai_message, HumanMessage.create("Tell me a joke.")]

    print("Usages:", usages)

    assert usages[0] is not None
    assert usages[0].cache_write_5m_tokens + usages[0].cached_input_tokens > 0
    assert usages[1] is not None and usages[1].cached_input_tokens > 0


@pytest.mark.costly
async def test_max_token_error(
    provider: AnthropicChatProvider,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider.settings.max_output_tokens = 20

    with pytest.raises(MaxTokenError):
        await _run(
            provider,
            [HumanMessage.create("Tell me a long story about AI.")],
            cost_recorder=cost_recorder,
            run_context=run_context,
        )


@pytest.mark.costly
@pytest.mark.parametrize("streaming", [False, True])
async def test_parallel_tool_calls_and_tool_results(
    provider: AnthropicChatProvider,
    image_file_info: ImageFileInfo,
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    class get_weather(BaseModel):
        """Get the weather of a city."""

        city: str

    class get_photo(BaseModel):
        """Get a photo of a city."""

        city: str

    tool_infos: list[ToolInfo] = [
        create_tool_info(get_weather),
        create_tool_info(get_photo),
    ]
    messages: list[Message] = [
        HumanMessage.create("Get the weather and a photo of Tokyo at the same time.")
    ]

    ai_messages = await _run(
        provider,
        messages,
        tool_infos=tool_infos,
        tool_choice="any",
        parallel_tool_calls=True,
        streaming=streaming,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
    ai_message = ai_messages[-1]

    print("tool_calls:", ai_message.tool_calls)

    assert isinstance(ai_message, AIMessage)
    assert ai_message.tool_calls

    messages.append(ai_message)
    messages += [
        ToolMessage.create(
            "Sunny, 25C" if tool_call.name == "get_weather" else "Here is the photo.",
            [] if tool_call.name == "get_weather" else [image_file_info],
            tool_name=tool_call.name,
            tool_call_id=tool_call.id,
        )
        for tool_call in ai_message.tool_calls
    ]

    ai_messages = await _run(
        provider,
        messages,
        tool_infos=tool_infos,
        streaming=streaming,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print(ai_messages[-1].to_text())

    assert ai_messages[-1].type == "ai"


@pytest.mark.costly
async def test_image_and_pdf(
    provider: AnthropicChatProvider,
    image_file_info: ImageFileInfo,
    pdf_file_info: PDFFileInfo,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    ai_messages = await _run(
        provider,
        [
            HumanMessage.create(
                "Describe the image and the PDF in one sentence each.",
                [image_file_info, pdf_file_info],
            )
        ],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print(ai_messages[-1].to_text())

    assert ai_messages[-1].to_text()
