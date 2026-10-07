from collections.abc import Callable
from typing import Any

import pytest
from google.genai import types
from pydantic import BaseModel

from kiarina.agi.chat_provider import (
    ChatProviderContext,
    ChatProviderState,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.chat_provider_impl.google_genai import (
    GoogleGenAIChatProvider,
    GoogleGenAIChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.google_genai._schemas.google_genai_usage import (
    GoogleGenAIUsage,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.file_info import (
    AudioFileInfo,
    ImageFileInfo,
    PDFFileInfo,
    VideoFileInfo,
)
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

MakeResponse = Callable[..., types.GenerateContentResponse]


def _create_provider(**kwargs: Any) -> GoogleGenAIChatProvider:
    provider = GoogleGenAIChatProvider(GoogleGenAIChatProviderSettings(**kwargs))
    provider.name = "google_genai"
    return provider


async def _run(
    provider: GoogleGenAIChatProvider,
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
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy")
    provider = _create_provider(model_name="gemini-test")

    assert str(provider) == "GoogleGenAIChatProvider(gemini-test)"
    assert provider.client is provider.client


def test_get_capabilities() -> None:
    capabilities = _create_provider(
        token_count_limit=2048, input_enabled={"image": True}
    ).get_capabilities()

    assert capabilities.token_count_limit == 2048
    assert capabilities.can_include("human", "image")
    assert not capabilities.can_include("human", "pdf")


def test_media_contents(
    image_file_blob: FileBlob,
    audio_file_blob: FileBlob,
    video_file_blob: FileBlob,
    pdf_file_blob: FileBlob,
) -> None:
    provider = _create_provider()

    for content in (
        provider.to_image_content(image_file_blob.mime_blob),
        provider.to_audio_content(audio_file_blob.mime_blob),
        provider.to_video_content(video_file_blob.mime_blob),
        provider.to_pdf_content(pdf_file_blob.mime_blob, display_name="a.pdf"),
    ):
        assert content is not None
        assert content["type"] == "inline_data"
        assert isinstance(content["data"], bytes)


# --------------------------------------------------
# Request
# --------------------------------------------------


@pytest.fixture
def ctx(run_context: RunContext) -> ChatProviderContext:
    return ChatProviderContext.create(
        messages=[SystemMessage.create("Be kind."), HumanMessage.create("Hello")],
        run_context=run_context,
    )


async def test_create_request(
    ctx: ChatProviderContext, tool_infos: list[ToolInfo]
) -> None:
    provider = _create_provider(model_name="gemini-test")
    ctx.tool_infos = tool_infos

    request = await provider.create_request(ctx)
    config = request["config"]

    assert request["model"] == "gemini-test"
    assert config.system_instruction == "Be kind."
    assert config.max_output_tokens == 65_536
    assert config.temperature == 0.0
    assert config.automatic_function_calling.disable is True
    assert config.tools[0].function_declarations[0].name == "get_weather"
    assert config.tool_config.function_calling_config.mode == "AUTO"


# --------------------------------------------------
# Invocation (fake client)
# --------------------------------------------------


class _FakeStream:
    def __init__(self, responses: list[types.GenerateContentResponse]) -> None:
        self.responses = responses

    def __aiter__(self) -> "_FakeStream":
        return self

    async def __anext__(self) -> types.GenerateContentResponse:
        if not self.responses:
            raise StopAsyncIteration
        return self.responses.pop(0)


class _FakeModels:
    def __init__(
        self,
        response: types.GenerateContentResponse,
        chunks: list[types.GenerateContentResponse] | None,
        error: Exception | None,
    ) -> None:
        self.response = response
        self.chunks = chunks if chunks is not None else [response]
        self.error = error

    async def generate_content(self, **kwargs: Any) -> types.GenerateContentResponse:
        if self.error:
            raise self.error
        return self.response

    async def generate_content_stream(self, **kwargs: Any) -> _FakeStream:
        if self.error:
            raise self.error
        return _FakeStream(list(self.chunks))


class _FakeClient:
    def __init__(
        self,
        response: types.GenerateContentResponse,
        chunks: list[types.GenerateContentResponse] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.models = _FakeModels(response, chunks, error)
        self.aio = self


def _usage(output_tokens: int = 5) -> dict[str, int]:
    return {"prompt_token_count": 10, "candidates_token_count": output_tokens}


@pytest.mark.parametrize("parallel_tool_calls", [None, True])
async def test_run_stream(
    make_response: MakeResponse,
    parallel_tool_calls: bool | None,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider = _create_provider()
    provider._client = _FakeClient(  # type: ignore[assignment]
        make_response(),
        chunks=[
            make_response([{"text": "Thinking", "thought": True}], finish_reason=None),
            make_response([{"text": "Hi"}], finish_reason=None),
            make_response(
                [
                    {"function_call": {"name": "f", "args": {"a": 1}}},
                    {"function_call": {"name": "g"}},
                ],
                usage=_usage(),
            ),
        ],
    )

    ai_messages = await _run(
        provider,
        [HumanMessage.create("Hello")],
        streaming=True,
        parallel_tool_calls=parallel_tool_calls,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert [m.to_text() for m in ai_messages[:1]] == ["Hi"]
    chunk_ids = [m.tool_call_chunks[0].id for m in ai_messages[1:3]]  # type: ignore[union-attr]
    result = ai_messages[-1]

    assert result.type == "ai"
    assert result.to_text().startswith("Hi")
    assert [tc.id for tc in result.tool_calls] == chunk_ids[
        : 2 if parallel_tool_calls else 1
    ]


async def test_run_invoke(
    make_response: MakeResponse,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider = _create_provider()
    provider._client = _FakeClient(  # type: ignore[assignment]
        make_response([{"text": "Hi"}], usage=_usage())
    )

    ai_messages = await _run(
        provider,
        [HumanMessage.create("Hello")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert ai_messages[-1].to_text() == "Hi"


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize(
    ("finish_reason", "output_tokens", "error_type"),
    [
        ("PROHIBITED_CONTENT", 5, SafetyError),
        ("MAX_TOKENS", 5, MaxTokenError),
        ("STOP", 100, MaxTokenError),
    ],
)
async def test_run_stop_reason_errors(
    make_response: MakeResponse,
    streaming: bool,
    finish_reason: str,
    output_tokens: int,
    error_type: type[Exception],
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider = _create_provider(max_output_tokens=100)
    provider._client = _FakeClient(  # type: ignore[assignment]
        make_response(finish_reason=finish_reason, usage=_usage(output_tokens))
    )

    with pytest.raises(error_type):
        await _run(
            provider,
            [HumanMessage.create("Hello")],
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize(
    ("message", "token_count"),
    [
        (
            "The input token count exceeds the maximum number of tokens allowed 1048576.",
            1_048_576,
        ),
        ("The input token count exceeds the maximum number of tokens allowed.", None),
        ("Something else", None),
    ],
)
async def test_run_request_errors(
    make_response: MakeResponse,
    streaming: bool,
    message: str,
    token_count: int | None,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider = _create_provider()
    provider._client = _FakeClient(  # type: ignore[assignment]
        make_response(), error=RuntimeError(message)
    )

    with pytest.raises((TokenOverflowError, RuntimeError)) as exc_info:
        await _run(
            provider,
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


# --------------------------------------------------
# Cost
# --------------------------------------------------


@pytest.mark.parametrize(
    ("prompt_tokens", "expected_microdollars"),
    [(200_000, 422_200), (200_001, 832_404)],
)
def test_get_cost_record(prompt_tokens: int, expected_microdollars: int) -> None:
    cost_record = _create_provider()._get_cost_record(
        GoogleGenAIUsage(
            prompt_tokens=prompt_tokens,
            cached_input_tokens=1_000,
            output_tokens=2_000,
        )
    )

    assert cost_record.microdollars == expected_microdollars
    assert cost_record.metadata == {
        "model_name": "gemini-3.1-pro-preview",
        "input_tokens": prompt_tokens - 1_000,
        "cached_input_tokens": 1_000,
        "output_tokens": 2_000,
    }


# --------------------------------------------------
# Use Cases (Gemini API)
# --------------------------------------------------


@pytest.fixture
def provider() -> GoogleGenAIChatProvider:
    return _create_provider(
        model_name="gemini-3.5-flash-lite",
        max_output_tokens=8_000,
        input_enabled={"image": True, "audio": True, "video": True, "pdf": True},
    )


@pytest.mark.costly
@pytest.mark.parametrize("streaming", [False, True])
async def test_hello(
    provider: GoogleGenAIChatProvider,
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
@pytest.mark.parametrize("streaming", [False, True])
async def test_parallel_tool_calls_and_tool_results(
    provider: GoogleGenAIChatProvider,
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    class get_weather(BaseModel):
        """Get the weather of a city."""

        city: str

    tool_infos: list[ToolInfo] = [create_tool_info(get_weather)]
    messages: list[Message] = [
        HumanMessage.create("Get the weather of Tokyo and Osaka, one call per city.")
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
            "Sunny, 25C", tool_name=tool_call.name, tool_call_id=tool_call.id
        )
        for tool_call in ai_message.tool_calls
    ]

    # NOTE: Gemini 3 rejects this turn unless function calls carry a signature.
    ai_messages = await _run(
        provider,
        messages,
        tool_infos=tool_infos,
        streaming=streaming,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print(ai_messages[-1].to_text())

    assert ai_messages[-1].to_text()


@pytest.mark.costly
async def test_media(
    provider: GoogleGenAIChatProvider,
    image_file_info: ImageFileInfo,
    audio_file_info: AudioFileInfo,
    video_file_info: VideoFileInfo,
    pdf_file_info: PDFFileInfo,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    ai_messages = await _run(
        provider,
        [
            HumanMessage.create(
                "Describe each attached file in one sentence.",
                [image_file_info, audio_file_info, video_file_info, pdf_file_info],
            )
        ],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print(ai_messages[-1].to_text())

    assert ai_messages[-1].to_text()


@pytest.mark.costly
async def test_max_token_error(
    provider: GoogleGenAIChatProvider,
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


async def test_thought_signature_state(
    make_response: MakeResponse,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider = _create_provider()
    provider._client = _FakeClient(  # type: ignore[assignment]
        make_response(
            [
                {
                    "function_call": {"id": "call_1", "name": "f"},
                    "thought_signature": b"sig",
                }
            ]
        )
    )

    [ai_message] = await _run(
        provider,
        [HumanMessage.create("Hello")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
    assert isinstance(ai_message, AIMessage)
    state = ChatProviderState.from_message(ai_message, "google_genai")
    assert state is not None

    request = await provider.create_request(
        ChatProviderContext.create(
            messages=[
                HumanMessage.create("Hello"),
                ai_message,
                ToolMessage.create("ok", tool_name="f", tool_call_id="call_1"),
            ],
            run_context=run_context,
        )
    )
    assert request["contents"][1].parts[0].thought_signature == b"sig"
