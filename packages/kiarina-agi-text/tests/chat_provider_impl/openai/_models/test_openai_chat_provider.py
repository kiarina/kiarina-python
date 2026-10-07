from collections.abc import AsyncIterator
from typing import Any

import pytest
from pydantic import BaseModel

from kiarina.agi.chat_provider import MaxTokenError, SafetyError, TokenOverflowError
from kiarina.agi.chat_provider_impl.openai import (
    OpenAIChatProvider,
    OpenAIChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.openai._schemas.openai_chat_result import (
    OpenAIChatResult,
)
from kiarina.agi.chat_provider_impl.openai._schemas.openai_usage import OpenAIUsage
from kiarina.agi.chat_provider_impl.openai._services.chat_completions_endpoint import (
    ChatCompletionsEndpoint,
)
from kiarina.agi.chat_provider_impl.openai._services.responses_endpoint import (
    ResponsesEndpoint,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.file_info import ImageFileInfo, PDFFileInfo
from kiarina.agi.message import AIMessage, AIMessageChunk, HumanMessage, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo, create_tool_info
from kiarina.utils.file import FileBlob

EndpointType = str


def _create_provider(**kwargs: Any) -> OpenAIChatProvider:
    provider = OpenAIChatProvider(OpenAIChatProviderSettings(**kwargs))
    provider.name = "openai"
    return provider


async def _run(
    provider: OpenAIChatProvider,
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


def test_endpoint() -> None:
    assert isinstance(_create_provider().endpoint, ChatCompletionsEndpoint)
    assert isinstance(
        _create_provider(endpoint_type="responses").endpoint, ResponsesEndpoint
    )


def test_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    provider = _create_provider(model_name="gpt-test", endpoint_type="responses")

    assert str(provider) == "OpenAIChatProvider(gpt-test, responses)"
    assert provider.client is provider.client
    print(f"openai_settings: {provider.openai_settings}")


def test_get_capabilities() -> None:
    capabilities = _create_provider(
        context_window=4096,
        max_output_tokens=1024,
        token_count_limit=2048,
        input_enabled={"image": True},
    ).get_capabilities()

    assert capabilities.token_count_limit == 2048
    assert capabilities.can_include("human", "image")
    assert not capabilities.can_include("human", "pdf")


# --------------------------------------------------
# Result Handling
# --------------------------------------------------


class _FakeEndpoint:
    def __init__(
        self, result: OpenAIChatResult | None = None, error: Exception | None = None
    ) -> None:
        self.result = result or OpenAIChatResult(ai_message=AIMessage.create("Hi"))
        self.error = error

    async def invoke(self, client: Any, ctx: Any) -> OpenAIChatResult:
        if self.error:
            raise self.error
        return self.result

    async def stream(
        self, client: Any, ctx: Any
    ) -> AsyncIterator[AIMessageChunk | OpenAIChatResult]:
        if self.error:
            raise self.error
        yield AIMessageChunk.create("Hi")
        yield self.result


@pytest.fixture
def fake_provider(monkeypatch: pytest.MonkeyPatch) -> OpenAIChatProvider:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    return _create_provider()


@pytest.mark.parametrize("streaming", [False, True])
async def test_run(
    fake_provider: OpenAIChatProvider,
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    fake_provider.endpoint = _FakeEndpoint(  # type: ignore[assignment]
        OpenAIChatResult(
            ai_message=AIMessage.create("Hi"),
            usage=OpenAIUsage(prompt_tokens=1_000, output_tokens=1_000),
        )
    )

    ai_messages = await _run(
        fake_provider,
        [HumanMessage.create("Hello")],
        streaming=streaming,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert len(ai_messages) == (2 if streaming else 1)
    assert ai_messages[-1].type == "ai"
    assert ai_messages[-1].to_text() == "Hi"


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize(
    ("stop_reason", "error_type"),
    [("content_filter", SafetyError), ("max_tokens", MaxTokenError)],
)
async def test_run_stop_reason_errors(
    fake_provider: OpenAIChatProvider,
    streaming: bool,
    stop_reason: Any,
    error_type: type[Exception],
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    fake_provider.endpoint = _FakeEndpoint(  # type: ignore[assignment]
        OpenAIChatResult(ai_message=AIMessage.create(""), stop_reason=stop_reason)
    )

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
    ("message", "error_type"),
    [
        (
            "This model's maximum context length is 1000 tokens. However, your "
            "messages resulted in 1200 tokens. Please reduce the length of the "
            "messages.",
            TokenOverflowError,
        ),
        ("Please reduce the length of the messages.", RuntimeError),
        ("Your input exceeds the context window of this model.", RuntimeError),
    ],
)
async def test_run_request_errors(
    fake_provider: OpenAIChatProvider,
    streaming: bool,
    message: str,
    error_type: type[Exception],
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    fake_provider.endpoint = _FakeEndpoint(error=RuntimeError(message))  # type: ignore[assignment]

    with pytest.raises(error_type) as exc_info:
        await _run(
            fake_provider,
            [HumanMessage.create("Hello")],
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    if isinstance(exc_info.value, TokenOverflowError):
        assert exc_info.value.token_count == 1200


@pytest.mark.parametrize(
    ("prompt_tokens", "expected_microdollars"),
    [
        (272_000, 27_335),
        (272_001, 54_571),
    ],
)
def test_get_cost_record_extended_pricing(
    prompt_tokens: int,
    expected_microdollars: int,
) -> None:
    provider = _create_provider(
        input_cost_microdollars_per_1k_tokens=100,
        cached_input_cost_microdollars_per_1k_tokens=10,
        output_cost_microdollars_per_1k_tokens=200,
        cache_write_cost_multiplier=1.25,
        extended_cost_threshold_tokens=272_000,
        extended_input_cost_multiplier=2.0,
        extended_output_cost_multiplier=1.5,
    )

    cost_record = provider._get_cost_record(
        OpenAIUsage(
            prompt_tokens=prompt_tokens,
            cached_input_tokens=1_000,
            cache_write_tokens=1_000,
            output_tokens=1_000,
        )
    )

    assert cost_record.microdollars == expected_microdollars
    assert cost_record.metadata == {
        "model_name": "gpt-5.5",
        "input_tokens": prompt_tokens - 2_000,
        "cache_write_tokens": 1_000,
        "cached_input_tokens": 1_000,
        "output_tokens": 1_000,
    }


def test_get_cost_record_cache_write_uses_input_cost_by_default() -> None:
    provider = _create_provider()

    without_cache_write = provider._get_cost_record(OpenAIUsage(prompt_tokens=1_001))
    with_cache_write = provider._get_cost_record(
        OpenAIUsage(prompt_tokens=1_001, cache_write_tokens=1_001)
    )

    assert without_cache_write.microdollars == 51
    assert with_cache_write.microdollars == 51
    assert with_cache_write.metadata.get("input_tokens") == 0
    assert with_cache_write.metadata.get("cache_write_tokens") == 1_001


# --------------------------------------------------
# Use Cases (OpenAI API)
# --------------------------------------------------

ENDPOINT_TYPES = ["chat_completions", "responses"]


@pytest.fixture(params=ENDPOINT_TYPES)
def provider(request: pytest.FixtureRequest) -> OpenAIChatProvider:
    return _create_provider(
        model_name="gpt-6-luna",
        endpoint_type=request.param,
        input_enabled={"image": True, "pdf": True},
    )


@pytest.mark.costly
@pytest.mark.parametrize("streaming", [False, True])
async def test_hello(
    provider: OpenAIChatProvider,
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
async def test_cost_record_with_cache(
    provider: OpenAIChatProvider,
    large_text_file_blob: FileBlob,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    messages: list[Message] = [
        HumanMessage.create(large_text_file_blob.raw_text),
        HumanMessage.create("Hello, how are you?"),
    ]
    usages: list[OpenAIUsage | None] = []

    for _ in range(2):
        result = await provider.endpoint.invoke(
            provider.client, _ctx(messages, run_context)
        )
        usages.append(result.usage)
        messages += [result.ai_message, HumanMessage.create("Tell me a joke.")]

    print("Usages:", usages)

    assert usages[0] is not None and usages[0].prompt_tokens > 0
    assert usages[1] is not None and usages[1].cached_input_tokens > 0


@pytest.mark.costly
async def test_max_token_error(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    for endpoint_type in ENDPOINT_TYPES:
        provider = _create_provider(
            model_name="gpt-6-luna",
            endpoint_type=endpoint_type,
            max_output_tokens=50,
            reasoning_effort="none",
        )

        with pytest.raises(MaxTokenError):
            await _run(
                provider,
                [HumanMessage.create("Tell me a long story about AI.")],
                cost_recorder=cost_recorder,
                run_context=run_context,
            )


@pytest.mark.costly
async def test_reasoning_effort_and_verbosity(
    provider: OpenAIChatProvider,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider.settings.reasoning_effort = "medium"
    provider.settings.verbosity = "low"

    ai_messages = await _run(
        provider,
        [HumanMessage.create("Hello")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print(ai_messages[-1].to_text())


@pytest.mark.costly
@pytest.mark.parametrize("streaming", [False, True])
async def test_parallel_tool_calls_and_tool_results(
    provider: OpenAIChatProvider,
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    from kiarina.agi.message import ToolMessage

    class WriteFile(BaseModel):
        """Write text to a file."""

        file_path: str
        text: str

    class CatFile(BaseModel):
        """Read the content of a file."""

        file_path: str

    tool_infos: list[ToolInfo] = [
        create_tool_info(WriteFile),
        create_tool_info(CatFile),
    ]
    messages: list[Message] = [
        HumanMessage.create(
            "./hello.txt に Hello と書いて、./hello.txt を CatFile して"
        )
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

    # The model may also call CatFile only after WriteFile has returned.
    assert isinstance(ai_message, AIMessage)
    assert ai_message.tool_calls[0].name == "WriteFile"
    assert ai_message.tool_calls[0].args["file_path"].endswith("hello.txt")

    messages.append(ai_message)
    messages += [
        ToolMessage.create(
            "Wrote." if tool_call.name == "WriteFile" else "Hello",
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
    print("tool_calls:", ai_messages[-1].tool_calls)

    assert ai_messages[-1].type == "ai"


@pytest.mark.costly
async def test_image_and_pdf(
    provider: OpenAIChatProvider,
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


def _ctx(messages: list[Message], run_context: RunContext) -> Any:
    from kiarina.agi.chat_provider import ChatProviderContext

    return ChatProviderContext.create(messages=messages, run_context=run_context)
