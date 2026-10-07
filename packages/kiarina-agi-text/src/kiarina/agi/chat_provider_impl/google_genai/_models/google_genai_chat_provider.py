import json
import math
import re
import uuid
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_content import ContentPart, MediaConverter
from kiarina.agi.chat_logger import chat_logger_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProviderContext,
    ChatProviderState,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
    collect_message_states,
    compute_message_hash,
)
from kiarina.agi.content import Content
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCallChunk
from kiarina.utils.mime import MIMEBlob

from .._operations.from_google_genai_response import from_google_genai_response
from .._operations.to_function_declarations import to_function_declarations
from .._operations.to_google_genai_request import to_google_genai_request
from .._operations.to_tool_config import to_tool_config
from .._schemas.google_genai_chat_result import GoogleGenAIChatResult
from .._schemas.google_genai_usage import GoogleGenAIUsage
from .._settings import GoogleGenAIChatProviderSettings

try:
    from google import genai
    from google.genai import types

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "google-genai and kiarina-lib-google are required to use "
        "GoogleGenAIChatProvider. "
        "Install them with: pip install 'kiarina-agi-text[chat-provider-google-genai]'"
    ) from exc


class GoogleGenAIChatProvider(BaseChatProvider, MediaConverter):
    """
    Google GenAI Chat Provider Implementation

    Calls Gemini with the google-genai SDK, through the Gemini API or Vertex AI
    as the Google settings select.
    """

    def __init__(self, settings: GoogleGenAIChatProviderSettings) -> None:
        super().__init__()

        self.settings: GoogleGenAIChatProviderSettings = settings
        self._client: genai.Client | None = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                **kiarina.lib.google.get_genai_options(
                    self.settings.google_auth_settings_key
                )
            )

        return self._client

    # --------------------------------------------------
    # Methods (ChatProvider)
    # --------------------------------------------------

    def get_capabilities(self) -> ChatCapabilities:
        return ChatCapabilities.model_validate(self.settings.model_dump())

    # --------------------------------------------------
    # Methods (MediaConverter)
    # --------------------------------------------------

    def to_image_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return _to_inline_data(mime_blob)

    def to_audio_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return _to_inline_data(mime_blob)

    def to_video_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return _to_inline_data(mime_blob)

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> ContentPart | None:
        return _to_inline_data(mime_blob)

    # --------------------------------------------------
    # Methods (BaseChatProvider)
    # --------------------------------------------------

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        request = await self.create_request(ctx)

        if ctx.streaming:
            async for ai_message in self._run_stream(ctx, request):
                yield ai_message
        else:
            yield await self._run_invoke(ctx, request)

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    async def create_request(self, ctx: ChatProviderContext) -> dict[str, Any]:
        states = collect_message_states(
            ctx.messages, self.name, model_name=self.settings.model_name
        )
        google_genai_request = await to_google_genai_request(
            ctx.messages,
            capabilities=ctx.capabilities,
            media_converter=self,
            run_context=ctx.run_context,
            thought_signatures={index: state.data for index, state in states.items()},
        )

        config: dict[str, Any] = {
            "max_output_tokens": self.settings.max_output_tokens,
            "temperature": self.settings.temperature,
            "automatic_function_calling": {"disable": True},
        }

        if google_genai_request.system_instruction:
            config["system_instruction"] = google_genai_request.system_instruction

        if ctx.tool_infos:
            config["tools"] = [
                {"function_declarations": to_function_declarations(ctx.tool_infos)}
            ]
            config["tool_config"] = to_tool_config(ctx.tool_choice, ctx.tool_infos)

        return {
            "model": self.settings.model_name,
            "contents": google_genai_request.contents,
            "config": types.GenerateContentConfig.model_validate(config),
        }

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    async def _run_invoke(
        self, ctx: ChatProviderContext, request: dict[str, Any]
    ) -> AIMessage:
        chat_logger = chat_logger_registry.resolve()
        chat_logger.log_chat_invoke_start(ctx.run_context)

        try:
            response = await self.client.aio.models.generate_content(**request)
        except Exception as e:
            if token_count := self._extract_overflow_token_count(e):
                raise TokenOverflowError(token_count) from e
            raise

        result = from_google_genai_response(response)
        chat_logger.log_chat_invoke_end(result.ai_message, ctx.run_context)
        return self._handle_result(ctx, result)

    async def _run_stream(
        self, ctx: ChatProviderContext, request: dict[str, Any]
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        chat_logger = chat_logger_registry.resolve()
        parts: list[Any] = []
        tool_call_ids: dict[int, str] = {}
        last: Any = None

        try:
            with chat_logger.log_chat_stream(ctx.run_context):
                stream = await self.client.aio.models.generate_content_stream(**request)

                async for response in stream:
                    last = response

                    for part in _candidate_parts(response):
                        parts.append(part)

                        if chunk := _to_ai_message_chunk(part, tool_call_ids):
                            chat_logger.log_chat_stream_chunk(chunk)
                            yield chunk
        except Exception as e:
            if token_count := self._extract_overflow_token_count(e):
                raise TokenOverflowError(token_count) from e
            raise

        if last is None:  # pragma: no cover
            raise AssertionError("Empty stream response")

        candidate = (last.candidates or [None])[0]
        final = types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(role="model", parts=parts),
                    finish_reason=candidate.finish_reason if candidate else None,
                )
            ],
            prompt_feedback=last.prompt_feedback,
            usage_metadata=last.usage_metadata,
        )

        result = from_google_genai_response(final, tool_call_ids=tool_call_ids)
        yield self._handle_result(ctx, result)

    def _handle_result(
        self, ctx: ChatProviderContext, result: GoogleGenAIChatResult
    ) -> AIMessage:
        ai_message = result.ai_message
        parallel_tool_calls = ctx.parallel_tool_calls

        if parallel_tool_calls is None:
            parallel_tool_calls = self.settings.parallel_tool_calls

        # NOTE: Gemini has no option to disable parallel function calls
        if parallel_tool_calls is False and len(ai_message.tool_calls) > 1:
            ai_message = ai_message.model_copy(
                update={"tool_calls": ai_message.tool_calls[:1]}
            )

        if result.usage:
            ctx.cost_recorder.add(self._get_cost_record(result.usage))

        if result.stop_reason == "safety":
            raise SafetyError()

        if result.stop_reason == "max_tokens" or (
            result.usage
            and result.usage.output_tokens >= self.settings.max_output_tokens
        ):
            raise MaxTokenError()

        tool_call_signatures = {
            tool_call.id: result.thought_signatures[tool_call.id]
            for tool_call in ai_message.tool_calls
            if tool_call.id in result.thought_signatures
        }

        if tool_call_signatures or result.text_thought_signature:
            # NOTE: Gemini 3 expects its thought signatures back with the turn.
            data: dict[str, Any] = {"tool_calls": tool_call_signatures}

            if result.text_thought_signature:
                data["text"] = result.text_thought_signature

            ChatProviderState(
                name=self.name,
                history_hash=compute_message_hash(
                    ai_message, model_name=self.settings.model_name
                ),
                data=data,
            ).write_to(ai_message)

        return ai_message

    def _extract_overflow_token_count(self, error: Exception) -> int | None:
        if (
            "The input token count exceeds the maximum number of tokens allowed"
            not in str(error)
        ):
            return None

        match = re.search(r"allowed (\d+)", str(error))
        return int(match.group(1)) if match else None

    def _get_cost_record(self, usage: GoogleGenAIUsage) -> CostRecord:
        input_tokens = usage.prompt_tokens - usage.cached_input_tokens

        if usage.prompt_tokens <= self.settings.threshold_tokens:
            input_cost = self.settings.input_cost_microdollars_per_1k_tokens
            cached_input_cost = (
                self.settings.cached_input_cost_microdollars_per_1k_tokens
            )
            output_cost = self.settings.output_cost_microdollars_per_1k_tokens
        else:
            input_cost = self.settings.extended_input_cost_microdollars_per_1k_tokens
            cached_input_cost = (
                self.settings.extended_cached_input_cost_microdollars_per_1k_tokens
            )
            output_cost = self.settings.extended_output_cost_microdollars_per_1k_tokens

        cost = math.ceil(
            input_cost * input_tokens / 1_000
            + cached_input_cost * usage.cached_input_tokens / 1_000
            + output_cost * usage.output_tokens / 1_000
        )

        return CostRecord(
            microdollars=cost,
            kind="chat",
            source=self.name,
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "cached_input_tokens": usage.cached_input_tokens,
                "output_tokens": usage.output_tokens,
            },
        )


def _to_inline_data(mime_blob: MIMEBlob) -> ContentPart:
    return {
        "type": "inline_data",
        "mime_type": mime_blob.mime_type,
        "data": mime_blob.raw_data,
    }


def _candidate_parts(response: Any) -> list[Any]:
    candidates = response.candidates or []

    if not candidates or not candidates[0].content:
        return []

    return list(candidates[0].content.parts or [])


def _to_ai_message_chunk(
    part: Any, tool_call_ids: dict[int, str]
) -> AIMessageChunk | None:
    """Gemini streams each function call whole, so one chunk carries all of it."""
    if part.function_call:
        index = len(tool_call_ids)
        tool_call_ids[index] = part.function_call.id or str(uuid.uuid4())

        return AIMessageChunk(
            contents=[Content(text="")],
            tool_call_chunks=[
                ToolCallChunk(
                    id=tool_call_ids[index],
                    name=part.function_call.name,
                    args=json.dumps(part.function_call.args or {}, ensure_ascii=False),
                    index=index,
                )
            ],
        )

    if part.text and not part.thought:
        return AIMessageChunk(contents=[Content(text=part.text)])

    return None
