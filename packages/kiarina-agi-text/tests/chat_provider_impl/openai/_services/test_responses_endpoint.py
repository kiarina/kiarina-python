from collections.abc import Callable
from typing import Any

import pytest
from openai.types.responses import Response

from kiarina.agi.chat_provider import ChatProviderContext
from kiarina.agi.chat_provider_impl.openai import OpenAIChatProviderSettings
from kiarina.agi.chat_provider_impl.openai._exceptions.openai_response_error import (
    OpenAIResponseError,
)
from kiarina.agi.chat_provider_impl.openai._schemas.openai_chat_result import (
    OpenAIChatResult,
)
from kiarina.agi.chat_provider_impl.openai._services.responses_endpoint import (
    ResponsesEndpoint,
)
from kiarina.agi.message import HumanMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo
from kiarina.utils.file import FileBlob


@pytest.fixture
def endpoint() -> ResponsesEndpoint:
    return ResponsesEndpoint(
        OpenAIChatProviderSettings(model_name="gpt-test", endpoint_type="responses")
    )


@pytest.fixture
def ctx(run_context: RunContext) -> ChatProviderContext:
    return ChatProviderContext.create(
        messages=[HumanMessage.create("Hello")], run_context=run_context
    )


def test_media_contents(
    endpoint: ResponsesEndpoint,
    image_file_blob: FileBlob,
    audio_file_blob: FileBlob,
    pdf_file_blob: FileBlob,
) -> None:
    image = endpoint.to_image_content(image_file_blob.mime_blob)
    pdf = endpoint.to_pdf_content(pdf_file_blob.mime_blob, display_name="a.pdf")

    assert image is not None and image["type"] == "input_image"
    assert pdf is not None and pdf["filename"] == "a.pdf"
    assert endpoint.to_audio_content(audio_file_blob.mime_blob) is None


async def test_create_request(
    endpoint: ResponsesEndpoint, ctx: ChatProviderContext
) -> None:
    assert await endpoint.create_request(ctx) == {
        "model": "gpt-test",
        "input": [{"role": "user", "content": "Hello"}],
        "max_output_tokens": 128_000,
        "temperature": 1.0,
        "store": False,
    }


async def test_create_request_with_options(
    endpoint: ResponsesEndpoint,
    ctx: ChatProviderContext,
    tool_infos: list[ToolInfo],
) -> None:
    endpoint.settings.reasoning_effort = "low"
    endpoint.settings.verbosity = "low"
    endpoint.settings.extra_body = {"foo": "bar"}
    ctx.tool_infos = tool_infos
    ctx.tool_choice = "get_weather"
    ctx.parallel_tool_calls = True

    request = await endpoint.create_request(ctx)

    assert request["reasoning"] == {"effort": "low"}
    assert request["text"] == {"verbosity": "low"}
    assert request["extra_body"] == {"foo": "bar"}
    assert request["tools"][0]["type"] == "function"
    assert request["tools"][0]["name"] == "get_weather"
    assert request["tools"][0]["strict"] is False
    assert request["tool_choice"] == {"type": "function", "name": "get_weather"}
    assert request["parallel_tool_calls"] is True


async def test_create_request_tool_choice_any(
    endpoint: ResponsesEndpoint,
    ctx: ChatProviderContext,
    tool_infos: list[ToolInfo],
) -> None:
    endpoint.settings.parallel_tool_calls = None
    ctx.tool_infos = tool_infos
    ctx.tool_choice = "any"

    request = await endpoint.create_request(ctx)

    assert request["tool_choice"] == "required"
    assert "parallel_tool_calls" not in request


class _Event:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


class _FakeStream:
    def __init__(self, events: list[_Event]) -> None:
        self.events = events

    def __aiter__(self) -> "_FakeStream":
        return self

    async def __anext__(self) -> _Event:
        if not self.events:
            raise StopAsyncIteration
        return self.events.pop(0)


class _FakeResponses:
    def __init__(self, response: Any) -> None:
        self.response = response

    async def create(self, **kwargs: Any) -> Any:
        return self.response


class _FakeClient:
    def __init__(self, response: Any) -> None:
        self.responses = _FakeResponses(response)


async def test_invoke(
    endpoint: ResponsesEndpoint,
    ctx: ChatProviderContext,
    make_response: Callable[..., Response],
) -> None:
    client = _FakeClient(make_response())
    result = await endpoint.invoke(client, ctx)  # type: ignore[arg-type]

    assert result.ai_message.to_text() == ""


async def test_stream(
    endpoint: ResponsesEndpoint,
    ctx: ChatProviderContext,
    make_response: Callable[..., Response],
) -> None:
    function_call = _Event(type="function_call", call_id="call_1", name="f")
    message = _Event(type="message")
    events = [
        _Event(type="response.created"),
        _Event(type="response.output_item.added", item=message, output_index=0),
        _Event(type="response.output_text.delta", delta="Hi"),
        _Event(type="response.output_item.added", item=function_call, output_index=1),
        _Event(
            type="response.function_call_arguments.delta", delta="{}", output_index=1
        ),
        _Event(type="response.completed", response=make_response()),
    ]

    client = _FakeClient(_FakeStream(events))
    items = [item async for item in endpoint.stream(client, ctx)]  # type: ignore[arg-type]

    assert items[0].contents[0].text == "Hi"  # type: ignore[union-attr]
    assert items[1].tool_call_chunks[0].name == "f"  # type: ignore[union-attr]
    assert items[2].tool_call_chunks[0].args == "{}"  # type: ignore[union-attr]
    assert isinstance(items[3], OpenAIChatResult)


async def test_stream_error(
    endpoint: ResponsesEndpoint, ctx: ChatProviderContext
) -> None:
    client = _FakeClient(
        _FakeStream([_Event(type="error", code="server_error", message="boom")])
    )

    with pytest.raises(OpenAIResponseError, match="server_error: boom"):
        _ = [item async for item in endpoint.stream(client, ctx)]  # type: ignore[arg-type]


async def test_stream_without_final_response(
    endpoint: ResponsesEndpoint, ctx: ChatProviderContext
) -> None:
    client = _FakeClient(_FakeStream([]))

    with pytest.raises(OpenAIResponseError, match="without a final response"):
        _ = [item async for item in endpoint.stream(client, ctx)]  # type: ignore[arg-type]
