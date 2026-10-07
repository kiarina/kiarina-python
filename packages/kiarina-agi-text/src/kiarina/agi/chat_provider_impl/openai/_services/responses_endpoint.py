from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from kiarina.agi.chat_content import ContentPart, MediaConverter
from kiarina.agi.chat_provider import ChatProviderContext
from kiarina.agi.content import Content
from kiarina.agi.message import AIMessageChunk, ToolCallChunk
from kiarina.utils.mime import MIMEBlob

from .._exceptions.openai_response_error import OpenAIResponseError
from .._operations.from_response import from_response
from .._operations.to_function_definitions import to_function_definitions
from .._operations.to_openai_tool_choice import to_openai_tool_choice
from .._operations.to_responses_input import to_responses_input
from .._schemas.openai_chat_result import OpenAIChatResult
from .._settings import OpenAIChatProviderSettings

if TYPE_CHECKING:
    from openai import AsyncOpenAI
    from openai.types.responses import Response


class ResponsesEndpoint(MediaConverter):
    """
    Responses API

    Requests are sent with `store=False`, so nothing is kept on the OpenAI side.
    Audio and video input are not supported.
    """

    def __init__(self, settings: OpenAIChatProviderSettings) -> None:
        self.settings: OpenAIChatProviderSettings = settings

    # --------------------------------------------------
    # Methods (MediaConverter)
    # --------------------------------------------------

    def to_image_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return {
            "type": "input_image",
            "image_url": mime_blob.raw_base64_url,
            "detail": "high",
        }

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> ContentPart | None:
        return {
            "type": "input_file",
            "filename": display_name,
            "file_data": mime_blob.raw_base64_url,
        }

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    async def invoke(
        self, client: "AsyncOpenAI", ctx: ChatProviderContext
    ) -> OpenAIChatResult:
        response = await client.responses.create(**await self.create_request(ctx))
        return from_response(response)

    async def stream(
        self, client: "AsyncOpenAI", ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | OpenAIChatResult]:
        final_response: Response | None = None

        stream = await client.responses.create(
            **await self.create_request(ctx), stream=True
        )

        async for event in stream:
            if event.type == "response.output_text.delta":
                yield AIMessageChunk(contents=[Content(text=event.delta)])

            elif event.type == "response.output_item.added":
                if event.item.type == "function_call":
                    yield AIMessageChunk(
                        contents=[Content(text="")],
                        tool_call_chunks=[
                            ToolCallChunk(
                                id=event.item.call_id,
                                name=event.item.name,
                                args="",
                                index=event.output_index,
                            )
                        ],
                    )

            elif event.type == "response.function_call_arguments.delta":
                yield AIMessageChunk(
                    contents=[Content(text="")],
                    tool_call_chunks=[
                        ToolCallChunk(args=event.delta, index=event.output_index)
                    ],
                )

            elif event.type in (
                "response.completed",
                "response.incomplete",
                "response.failed",
            ):
                final_response = event.response

            elif event.type == "error":
                raise OpenAIResponseError(f"{event.code}: {event.message}")

        if final_response is None:
            raise OpenAIResponseError("Stream ended without a final response")

        yield from_response(final_response)

    async def create_request(self, ctx: ChatProviderContext) -> dict[str, Any]:
        request: dict[str, Any] = {
            "model": self.settings.model_name,
            "input": await to_responses_input(
                ctx.messages,
                capabilities=ctx.capabilities,
                media_converter=self,
                run_context=ctx.run_context,
            ),
            "max_output_tokens": self.settings.max_output_tokens,
            "temperature": self.settings.temperature,
            "store": False,
        }

        if self.settings.reasoning_effort:
            request["reasoning"] = {"effort": self.settings.reasoning_effort}

        if self.settings.verbosity:
            request["text"] = {"verbosity": self.settings.verbosity}

        if self.settings.extra_body:
            request["extra_body"] = self.settings.extra_body

        if ctx.tool_infos:
            request["tools"] = [
                {"type": "function", "strict": False, **definition}
                for definition in to_function_definitions(ctx.tool_infos)
            ]

            tool_choice = to_openai_tool_choice(ctx.tool_choice)

            if tool_choice in ("auto", "required"):
                request["tool_choice"] = tool_choice
            else:
                request["tool_choice"] = {"type": "function", "name": tool_choice}

            parallel_tool_calls = ctx.parallel_tool_calls

            if parallel_tool_calls is None:
                parallel_tool_calls = self.settings.parallel_tool_calls

            if parallel_tool_calls is not None:
                request["parallel_tool_calls"] = parallel_tool_calls

        return request
