from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from kiarina.agi.chat_content import ContentPart, MediaConverter
from kiarina.agi.chat_provider import ChatProviderContext
from kiarina.agi.message import AIMessageChunk
from kiarina.utils.mime import MIMEBlob

from .._models.chat_completions_stream_accumulator import (
    ChatCompletionsStreamAccumulator,
)
from .._operations.from_chat_completion import from_chat_completion
from .._operations.to_chat_completions_messages import to_chat_completions_messages
from .._operations.to_function_definitions import to_function_definitions
from .._operations.to_openai_tool_choice import to_openai_tool_choice
from .._schemas.openai_chat_result import OpenAIChatResult
from .._settings import OpenAIChatProviderSettings

if TYPE_CHECKING:
    from openai import AsyncOpenAI


class ChatCompletionsEndpoint(MediaConverter):
    """
    Chat Completions API

    NOTE: `input_audio` and `video_url` are for OpenAI-compatible servers such as
    vLLM. The OpenAI API itself rejects video input.
    """

    def __init__(self, settings: OpenAIChatProviderSettings) -> None:
        self.settings: OpenAIChatProviderSettings = settings

    # --------------------------------------------------
    # Methods (MediaConverter)
    # --------------------------------------------------

    def to_image_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return {
            "type": "image_url",
            "image_url": {"url": mime_blob.raw_base64_url, "detail": "high"},
        }

    def to_audio_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return {
            "type": "input_audio",
            "input_audio": {
                "data": mime_blob.raw_base64_str,
                "format": mime_blob.mime_type.split("/")[1],
            },
        }

    def to_video_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return {"type": "video_url", "video_url": {"url": mime_blob.raw_base64_url}}

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> ContentPart | None:
        return {
            "type": "file",
            "file": {"filename": display_name, "file_data": mime_blob.raw_base64_url},
        }

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    async def invoke(
        self, client: "AsyncOpenAI", ctx: ChatProviderContext
    ) -> OpenAIChatResult:
        completion = await client.chat.completions.create(
            **await self.create_request(ctx)
        )
        return from_chat_completion(completion)

    async def stream(
        self, client: "AsyncOpenAI", ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | OpenAIChatResult]:
        accumulator = ChatCompletionsStreamAccumulator()

        stream = await client.chat.completions.create(
            **await self.create_request(ctx),
            stream=True,
            stream_options={"include_usage": True},
        )

        async for chunk in stream:
            if ai_message_chunk := accumulator.add(chunk):
                yield ai_message_chunk

        yield accumulator.to_result()

    async def create_request(self, ctx: ChatProviderContext) -> dict[str, Any]:
        request: dict[str, Any] = {
            "model": self.settings.model_name,
            "messages": await to_chat_completions_messages(
                ctx.messages,
                capabilities=ctx.capabilities,
                media_converter=self,
                run_context=ctx.run_context,
            ),
            "max_completion_tokens": self.settings.max_output_tokens,
        }

        if self.settings.temperature is not None:
            request["temperature"] = self.settings.temperature

        if self.settings.reasoning_effort:
            request["reasoning_effort"] = self.settings.reasoning_effort

        if self.settings.verbosity:
            request["verbosity"] = self.settings.verbosity

        if self.settings.extra_body:
            request["extra_body"] = self.settings.extra_body

        if ctx.tool_infos:
            request["tools"] = [
                {"type": "function", "function": definition}
                for definition in to_function_definitions(ctx.tool_infos)
            ]

            tool_choice = to_openai_tool_choice(ctx.tool_choice)

            if tool_choice in ("auto", "required"):
                request["tool_choice"] = tool_choice
            else:
                request["tool_choice"] = {
                    "type": "function",
                    "function": {"name": tool_choice},
                }

            parallel_tool_calls = ctx.parallel_tool_calls

            if parallel_tool_calls is None:
                parallel_tool_calls = self.settings.parallel_tool_calls

            if parallel_tool_calls is not None:
                request["parallel_tool_calls"] = parallel_tool_calls

        return request
