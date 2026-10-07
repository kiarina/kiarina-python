from collections.abc import Callable
from typing import Any

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from kiarina.agi.chat_provider import ChatProviderContext
from kiarina.agi.chat_provider_impl.openai import OpenAIChatProviderSettings
from kiarina.agi.chat_provider_impl.openai._schemas.openai_chat_result import (
    OpenAIChatResult,
)
from kiarina.agi.chat_provider_impl.openai._services.chat_completions_endpoint import (
    ChatCompletionsEndpoint,
)
from kiarina.agi.message import HumanMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo
from kiarina.utils.file import FileBlob


@pytest.fixture
def endpoint() -> ChatCompletionsEndpoint:
    return ChatCompletionsEndpoint(OpenAIChatProviderSettings(model_name="gpt-test"))


@pytest.fixture
def ctx(run_context: RunContext) -> ChatProviderContext:
    return ChatProviderContext.create(
        messages=[HumanMessage.create("Hello")], run_context=run_context
    )


def test_media_contents(
    endpoint: ChatCompletionsEndpoint,
    image_file_blob: FileBlob,
    audio_file_blob: FileBlob,
    video_file_blob: FileBlob,
    pdf_file_blob: FileBlob,
) -> None:
    image = endpoint.to_image_content(image_file_blob.mime_blob)
    audio = endpoint.to_audio_content(audio_file_blob.mime_blob)
    video = endpoint.to_video_content(video_file_blob.mime_blob)
    pdf = endpoint.to_pdf_content(pdf_file_blob.mime_blob, display_name="a.pdf")

    assert image is not None and image["type"] == "image_url"
    assert audio is not None and audio["type"] == "input_audio"
    assert video is not None and video["type"] == "video_url"
    assert pdf is not None and pdf["file"]["filename"] == "a.pdf"


async def test_create_request(
    endpoint: ChatCompletionsEndpoint, ctx: ChatProviderContext
) -> None:
    request = await endpoint.create_request(ctx)

    assert request == {
        "model": "gpt-test",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_completion_tokens": 128_000,
        "temperature": 1.0,
    }


async def test_create_request_with_options(
    endpoint: ChatCompletionsEndpoint,
    ctx: ChatProviderContext,
    tool_infos: list[ToolInfo],
) -> None:
    endpoint.settings.reasoning_effort = "low"
    endpoint.settings.verbosity = "low"
    endpoint.settings.extra_body = {"chat_template_kwargs": {"enable_thinking": True}}
    ctx.tool_infos = tool_infos
    ctx.tool_choice = "get_weather"

    request = await endpoint.create_request(ctx)

    assert request["reasoning_effort"] == "low"
    assert request["verbosity"] == "low"
    assert request["extra_body"] == {"chat_template_kwargs": {"enable_thinking": True}}
    assert request["tools"][0]["type"] == "function"
    assert request["tools"][0]["function"]["name"] == "get_weather"
    assert request["tool_choice"] == {
        "type": "function",
        "function": {"name": "get_weather"},
    }
    assert request["parallel_tool_calls"] is False


async def test_create_request_tool_choice_any(
    endpoint: ChatCompletionsEndpoint,
    ctx: ChatProviderContext,
    tool_infos: list[ToolInfo],
) -> None:
    endpoint.settings.parallel_tool_calls = None
    ctx.tool_infos = tool_infos
    ctx.tool_choice = "any"

    request = await endpoint.create_request(ctx)

    assert request["tool_choice"] == "required"
    assert "parallel_tool_calls" not in request


class _FakeStream:
    def __init__(self, chunks: list[ChatCompletionChunk]) -> None:
        self.chunks = chunks

    def __aiter__(self) -> "_FakeStream":
        return self

    async def __anext__(self) -> ChatCompletionChunk:
        if not self.chunks:
            raise StopAsyncIteration
        return self.chunks.pop(0)


class _FakeCompletions:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.kwargs: dict[str, Any] = {}

    async def create(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        return self.response


class _FakeClient:
    def __init__(self, response: Any) -> None:
        self.completions = _FakeCompletions(response)
        self.chat = self


async def test_invoke(
    endpoint: ChatCompletionsEndpoint,
    ctx: ChatProviderContext,
    make_completion: Callable[..., ChatCompletion],
) -> None:
    client = _FakeClient(make_completion({"content": "Hi"}))
    result = await endpoint.invoke(client, ctx)  # type: ignore[arg-type]

    assert result.ai_message.to_text() == "Hi"


async def test_stream(
    endpoint: ChatCompletionsEndpoint,
    ctx: ChatProviderContext,
    make_chunk: Callable[..., ChatCompletionChunk],
) -> None:
    client = _FakeClient(
        _FakeStream([make_chunk({"content": "Hi"}), make_chunk(finish_reason="stop")])
    )
    items = [item async for item in endpoint.stream(client, ctx)]  # type: ignore[arg-type]

    assert client.completions.kwargs["stream"] is True
    assert client.completions.kwargs["stream_options"] == {"include_usage": True}
    assert isinstance(items[-1], OpenAIChatResult)
    assert items[-1].ai_message.to_text() == "Hi"


async def test_create_request_without_temperature(
    endpoint: ChatCompletionsEndpoint, ctx: ChatProviderContext
) -> None:
    endpoint.settings.temperature = None

    assert "temperature" not in await endpoint.create_request(ctx)
