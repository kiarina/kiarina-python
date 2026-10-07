import math
import re
from collections.abc import AsyncIterator

from kiarina.agi.chat_logger import chat_logger_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProviderContext,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk

from .._schemas.openai_chat_result import OpenAIChatResult
from .._schemas.openai_usage import OpenAIUsage
from .._services.chat_completions_endpoint import ChatCompletionsEndpoint
from .._services.responses_endpoint import ResponsesEndpoint
from .._settings import OpenAIChatProviderSettings

try:
    from openai import AsyncOpenAI

    import kiarina.lib.openai
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-openai and openai are required to use OpenAIChatProvider. "
        "Install them with: pip install 'kiarina-agi-text[chat-provider-openai]'"
    ) from exc


class OpenAIChatProvider(BaseChatProvider):
    """
    OpenAI Chat Provider Implementation

    Calls the Chat Completions API or the Responses API with the OpenAI SDK,
    as selected by `endpoint_type`.
    """

    def __init__(self, settings: OpenAIChatProviderSettings) -> None:
        super().__init__()

        self.settings: OpenAIChatProviderSettings = settings
        self.endpoint: ChatCompletionsEndpoint | ResponsesEndpoint = (
            ResponsesEndpoint(settings)
            if settings.endpoint_type == "responses"
            else ChatCompletionsEndpoint(settings)
        )
        self._client: AsyncOpenAI | None = None

    def __str__(self) -> str:
        props: list[str] = [
            self.settings.model_name,
            self.settings.endpoint_type,
        ]

        return f"{self.__class__.__name__}({', '.join(props)})"

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def openai_settings(self) -> kiarina.lib.openai.OpenAISettings:
        return kiarina.lib.openai.settings_manager.get_settings(
            self.settings.openai_settings_key
        )

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                timeout=self.settings.timeout,
                **self.openai_settings.to_client_kwargs(),
            )

        return self._client

    # --------------------------------------------------
    # Methods (ChatProvider)
    # --------------------------------------------------

    def get_capabilities(self) -> ChatCapabilities:
        return ChatCapabilities.model_validate(self.settings.model_dump())

    # --------------------------------------------------
    # Methods (BaseChatProvider)
    # --------------------------------------------------

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        if ctx.streaming:
            async for ai_message in self._run_stream(ctx):
                yield ai_message
        else:
            yield await self._run_invoke(ctx)

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    async def _run_invoke(self, ctx: ChatProviderContext) -> AIMessage:
        chat_logger = chat_logger_registry.resolve()
        chat_logger.log_chat_invoke_start(ctx.run_context)

        try:
            result = await self.endpoint.invoke(self.client, ctx)
        except Exception as e:
            if token_count := self._extract_overflow_token_count(e):
                raise TokenOverflowError(token_count) from e
            raise

        chat_logger.log_chat_invoke_end(result.ai_message, ctx.run_context)
        return self._handle_result(ctx, result)

    async def _run_stream(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        chat_logger = chat_logger_registry.resolve()
        result: OpenAIChatResult | None = None

        try:
            with chat_logger.log_chat_stream(ctx.run_context):
                async for item in self.endpoint.stream(self.client, ctx):
                    if isinstance(item, OpenAIChatResult):
                        result = item
                    else:
                        chat_logger.log_chat_stream_chunk(item)
                        yield item
        except Exception as e:
            if token_count := self._extract_overflow_token_count(e):
                raise TokenOverflowError(token_count) from e
            raise

        if result is None:  # pragma: no cover
            raise AssertionError("Empty stream response")

        yield self._handle_result(ctx, result)

    def _handle_result(
        self, ctx: ChatProviderContext, result: OpenAIChatResult
    ) -> AIMessage:
        if result.usage:
            ctx.cost_recorder.add(self._get_cost_record(result.usage))

        if result.stop_reason == "content_filter":
            raise SafetyError()

        if result.stop_reason == "max_tokens":
            raise MaxTokenError()

        return result.ai_message

    def _extract_overflow_token_count(self, error: Exception) -> int | None:
        if "Please reduce the length of the messages" not in str(error):
            return None

        match = re.search(r"resulted in\s+(\d+)\s+tokens", str(error))
        return int(match.group(1)) if match else None

    def _get_cost_record(self, usage: OpenAIUsage) -> CostRecord:
        input_tokens = (
            usage.prompt_tokens - usage.cached_input_tokens - usage.cache_write_tokens
        )

        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        cached_input_cost = self.settings.cached_input_cost_microdollars_per_1k_tokens
        output_cost = self.settings.output_cost_microdollars_per_1k_tokens

        input_multiplier = 1.0
        output_multiplier = 1.0
        threshold = self.settings.extended_cost_threshold_tokens

        if threshold is not None and usage.prompt_tokens > threshold:
            input_multiplier = self.settings.extended_input_cost_multiplier
            output_multiplier = self.settings.extended_output_cost_multiplier

        cost = math.ceil(
            input_cost * input_multiplier * input_tokens / 1_000
            + input_cost
            * self.settings.cache_write_cost_multiplier
            * input_multiplier
            * usage.cache_write_tokens
            / 1_000
            + cached_input_cost * input_multiplier * usage.cached_input_tokens / 1_000
            + output_cost * output_multiplier * usage.output_tokens / 1_000
        )

        return CostRecord(
            microdollars=cost,
            kind="chat",
            source=self.name,
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "cache_write_tokens": usage.cache_write_tokens,
                "cached_input_tokens": usage.cached_input_tokens,
                "output_tokens": usage.output_tokens,
            },
        )
