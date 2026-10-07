import logging
import math
import re
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
    compute_message_hashes,
)
from kiarina.agi.content import Content
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk, ToolCallChunk
from kiarina.utils.mime import MIMEBlob

from .._constants.no_forced_tool_choice_model_prefixes import (
    NO_FORCED_TOOL_CHOICE_MODEL_PREFIXES,
)
from .._operations.append_tool_choice_instruction import (
    append_tool_choice_instruction,
)
from .._operations.from_anthropic_message import from_anthropic_message
from .._operations.to_anthropic_request import to_anthropic_request
from .._operations.to_anthropic_tool_choice import to_anthropic_tool_choice
from .._operations.to_anthropic_tools import to_anthropic_tools
from .._schemas.anthropic_chat_result import AnthropicChatResult
from .._schemas.anthropic_usage import AnthropicUsage
from .._settings import AnthropicChatProviderSettings

try:
    from anthropic import AsyncAnthropic

    import kiarina.lib.anthropic
except ImportError as exc:
    raise ImportError(
        "anthropic and kiarina-lib-anthropic are required to use "
        "AnthropicChatProvider. "
        "Install them with: pip install 'kiarina-agi-text[chat-provider-anthropic]'"
    ) from exc

logger = logging.getLogger(__name__)


class AnthropicChatProvider(BaseChatProvider, MediaConverter):
    """
    Anthropic Chat Provider Implementation

    Calls the Messages API with the Anthropic SDK. Subclasses change the API
    host by overriding `_create_client`.
    """

    def __init__(self, settings: AnthropicChatProviderSettings) -> None:
        super().__init__()

        self.settings: AnthropicChatProviderSettings = settings
        self._client: Any = None

    def __str__(self) -> str:
        props: list[str] = [self.settings.model_name]

        if self.settings.context_1m_enabled:
            props.append("context_1m")

        return f"{self.__class__.__name__}({', '.join(props)})"

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def anthropic_settings(self) -> kiarina.lib.anthropic.AnthropicSettings:
        return kiarina.lib.anthropic.settings_manager.get_settings(
            self.settings.anthropic_settings_key
        )

    @property
    def token_count_model_name(self) -> str:
        return self.settings.token_count_model_name or self.settings.model_name

    @property
    def client(self) -> AsyncAnthropic:
        """`AsyncAnthropic`, or a client with the same interface for other hosts."""
        if self._client is None:
            self._client = self._create_client()

        return self._client  # type: ignore[no-any-return]

    # --------------------------------------------------
    # Methods (ChatProvider)
    # --------------------------------------------------

    def get_capabilities(self) -> ChatCapabilities:
        return ChatCapabilities.model_validate(self.settings.model_dump())

    # --------------------------------------------------
    # Methods (MediaConverter)
    # --------------------------------------------------

    def to_image_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_blob.mime_type,
                "data": mime_blob.raw_base64_str,
            },
        }

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> ContentPart | None:
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": mime_blob.raw_base64_str,
            },
        }

    # --------------------------------------------------
    # Methods (BaseChatProvider)
    # --------------------------------------------------

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        request = await self.create_request(ctx)
        await self._check_token_overflow(request)

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
        anthropic_request = await to_anthropic_request(
            ctx.messages,
            model_name=self.settings.model_name,
            capabilities=ctx.capabilities,
            media_converter=self,
            run_context=ctx.run_context,
            thinking_blocks={
                index: state.data.get("thinking_blocks", [])
                for index, state in states.items()
            },
        )

        request: dict[str, Any] = {
            "model": self.settings.model_name,
            "messages": anthropic_request.messages,
            "max_tokens": self.settings.max_output_tokens,
        }

        if anthropic_request.system is not None:
            request["system"] = anthropic_request.system

        if self.settings.temperature is not None:
            # NOTE: Anthropic SDK 1.x does not accept `temperature` as a keyword.
            request["extra_body"] = {"temperature": self.settings.temperature}

        if self.settings.context_1m_enabled:
            request["extra_headers"] = {"anthropic-beta": "context-1m-2025-08-07"}

        if ctx.tool_infos:
            parallel_tool_calls = ctx.parallel_tool_calls

            if parallel_tool_calls is None:
                parallel_tool_calls = self.settings.parallel_tool_calls

            request["tools"] = to_anthropic_tools(
                ctx.tool_infos, cache_ttl=self.settings.cache_ttl
            )
            forced_tool_choice_supported = not self.settings.model_name.startswith(
                NO_FORCED_TOOL_CHOICE_MODEL_PREFIXES
            )
            request["tool_choice"] = to_anthropic_tool_choice(
                ctx.tool_choice,
                parallel_tool_calls=parallel_tool_calls,
                forced_tool_choice_supported=forced_tool_choice_supported,
            )

            if not forced_tool_choice_supported:
                append_tool_choice_instruction(request["messages"], ctx.tool_choice)

        return request

    # --------------------------------------------------
    # Protected Methods
    # --------------------------------------------------

    def _create_client(self) -> Any:
        client_kwargs: dict[str, Any] = {}

        if self.anthropic_settings.api_key is not None:
            client_kwargs["api_key"] = (
                self.anthropic_settings.api_key.get_secret_value()
            )

        if self.anthropic_settings.base_url:
            client_kwargs["base_url"] = self.anthropic_settings.base_url

        return AsyncAnthropic(
            timeout=self.settings.timeout,
            max_retries=self.settings.max_retry_count,
            **client_kwargs,
        )

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    async def _run_invoke(
        self, ctx: ChatProviderContext, request: dict[str, Any]
    ) -> AIMessage:
        chat_logger = chat_logger_registry.resolve()
        chat_logger.log_chat_invoke_start(ctx.run_context)

        try:
            message = await self.client.messages.create(**request)
        except Exception as e:
            if token_count := self._extract_overflow_token_count(e):
                raise TokenOverflowError(token_count) from e
            raise

        result = from_anthropic_message(message, cache_ttl=self.settings.cache_ttl)
        chat_logger.log_chat_invoke_end(result.ai_message, ctx.run_context)
        return self._handle_result(ctx, result)

    async def _run_stream(
        self, ctx: ChatProviderContext, request: dict[str, Any]
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        chat_logger = chat_logger_registry.resolve()

        try:
            with chat_logger.log_chat_stream(ctx.run_context):
                async with self.client.messages.stream(**request) as stream:
                    async for event in stream:
                        if chunk := _to_ai_message_chunk(event):
                            chat_logger.log_chat_stream_chunk(chunk)
                            yield chunk

                    message = await stream.get_final_message()
        except Exception as e:
            if token_count := self._extract_overflow_token_count(e):
                raise TokenOverflowError(token_count) from e
            raise

        result = from_anthropic_message(message, cache_ttl=self.settings.cache_ttl)
        yield self._handle_result(ctx, result)

    def _handle_result(
        self, ctx: ChatProviderContext, result: AnthropicChatResult
    ) -> AIMessage:
        if result.usage:
            ctx.cost_recorder.add(self._get_cost_record(result.usage))

        if result.stop_reason == "refusal":
            raise SafetyError()

        if result.stop_reason == "max_tokens":
            raise MaxTokenError()

        if result.thinking_blocks:
            # NOTE: Thinking blocks are sent back with this turn, as the models
            # with thinking always on ask for.
            ChatProviderState(
                name=self.name,
                history_hash=compute_message_hashes(
                    [*ctx.messages, result.ai_message],
                    model_name=self.settings.model_name,
                )[-1],
                data={"thinking_blocks": result.thinking_blocks},
            ).write_to(result.ai_message)

        return result.ai_message

    async def _check_token_overflow(self, request: dict[str, Any]) -> None:
        count_kwargs: dict[str, Any] = {
            "model": self.token_count_model_name,
            "messages": request["messages"],
        }

        for key in ("system", "tools", "extra_headers"):
            if key in request:
                count_kwargs[key] = request[key]

        try:
            # NOTE: Never retry. Vertex AI often has little count-tokens quota,
            # and a failed count only skips the check.
            result = await self.client.with_options(
                max_retries=0
            ).messages.count_tokens(**count_kwargs)
        except Exception as e:
            # NOTE: Ignore errors and attempt the API request
            logger.debug("Failed to count tokens: %s", e)
            return

        if result.input_tokens > self.settings.token_count_limit:
            raise TokenOverflowError(result.input_tokens)

    def _extract_overflow_token_count(self, error: Exception) -> int | None:
        message = str(error)

        if "prompt is too long" in message:
            match = re.search(r"prompt is too long:\s*(\d+)\s*tokens", message)
        elif "exceed context limit" in message:
            match = re.search(r"context limit:\s*(\d+)\s*\+", message)
        elif "Token overflow error" in message:
            match = re.search(r"Token overflow error:\s*(\d+)\s*tokens", message)
        else:
            match = None

        return int(match.group(1)) if match else None

    def _get_cost_record(self, usage: AnthropicUsage) -> CostRecord:
        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        cache_write_5m_cost = (
            self.settings.cache_write_5m_cost_microdollars_per_1k_tokens
        )
        cache_write_1h_cost = (
            self.settings.cache_write_1h_cost_microdollars_per_1k_tokens
        )
        cached_input_cost = self.settings.cached_input_cost_microdollars_per_1k_tokens
        output_cost = self.settings.output_cost_microdollars_per_1k_tokens

        multiplier_input = 1.0
        multiplier_output = 1.0

        if (
            self.settings.context_1m_enabled
            and usage.input_tokens >= self.settings.context_1m_threshold_tokens
        ):
            multiplier_input = self.settings.context_1m_input_cost_multiplier
            multiplier_output = self.settings.context_1m_output_cost_multiplier

        # fmt: off
        cost = math.ceil(
            input_cost * multiplier_input * usage.input_tokens / 1_000
            + cache_write_5m_cost * multiplier_input * usage.cache_write_5m_tokens / 1_000
            + cache_write_1h_cost * multiplier_input * usage.cache_write_1h_tokens / 1_000
            + cached_input_cost * multiplier_input * usage.cached_input_tokens / 1_000
            + output_cost * multiplier_output * usage.output_tokens / 1_000
        )
        # fmt: on

        return CostRecord(
            microdollars=cost,
            kind="chat",
            source=self.name,
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": usage.input_tokens,
                "cache_write_5m_tokens": usage.cache_write_5m_tokens,
                "cache_write_1h_tokens": usage.cache_write_1h_tokens,
                "cached_input_tokens": usage.cached_input_tokens,
                "output_tokens": usage.output_tokens,
            },
        )


def _to_ai_message_chunk(event: Any) -> AIMessageChunk | None:
    """Use the raw block events only. The SDK also emits derived `text` events."""
    if event.type == "content_block_start" and event.content_block.type == "tool_use":
        return AIMessageChunk(
            contents=[Content(text="")],
            tool_call_chunks=[
                ToolCallChunk(
                    id=event.content_block.id,
                    name=event.content_block.name,
                    args="",
                    index=event.index,
                )
            ],
        )

    if event.type == "content_block_delta":
        if event.delta.type == "text_delta":
            return AIMessageChunk(contents=[Content(text=event.delta.text)])

        if event.delta.type == "input_json_delta":
            return AIMessageChunk(
                contents=[Content(text="")],
                tool_call_chunks=[
                    ToolCallChunk(args=event.delta.partial_json, index=event.index)
                ],
            )

    return None
