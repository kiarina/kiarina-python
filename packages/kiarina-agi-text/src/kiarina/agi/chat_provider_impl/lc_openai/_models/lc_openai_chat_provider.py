import logging
import math
import re
from collections.abc import AsyncIterator
from typing import Any, cast

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProvider,
    LangChainChatProviderContext,
    LCAIMessage,
    LCAIMessageChunk,
    LCMessage,
    has_content,
    normalize_content,
    remove_content,
)
from kiarina.utils.mime import MIMEBlob

from .._settings import LCOpenAIChatProviderSettings

try:
    from langchain.chat_models import BaseChatModel
    from langchain_core.language_models import LanguageModelInput
    from langchain_core.runnables import Runnable
    from langchain_openai import ChatOpenAI

    import kiarina.lib.openai
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-openai and langchain-openai are required to use "
        "LCOpenAIChatProvider. "
        "Install them with: pip install 'kiarina-agi-text[chat-provider-lc-openai]'"
    ) from exc

logger = logging.getLogger(__name__)


class LCOpenAIChatProvider(LangChainChatProvider):
    """
    LangChain OpenAI Chat Provider Implementation

    NOTE: Behavior
    - Primarily uses the Chat Completion API
    - Switches to Responses API only when PDF input is present

    NOTE: Image input in Tool messages
    - Chat Completion API: Available for models other than gpt-4o
    - Response API: Not available for any models
    """

    def __init__(self, settings: LCOpenAIChatProviderSettings) -> None:
        super().__init__()

        self.settings: LCOpenAIChatProviderSettings = settings
        self.use_responses_api: bool = False

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

    # --------------------------------------------------
    # Methods (ChatProvider)
    # --------------------------------------------------

    def get_capabilities(self) -> ChatCapabilities:
        return ChatCapabilities.model_validate(self.settings.model_dump())

    # --------------------------------------------------
    # Methods (LangChainMediaConverter)
    # --------------------------------------------------

    def to_image_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        return {
            "type": "image_url",
            "image_url": {
                "url": mime_blob.raw_base64_url,
                "detail": "high",
            },
        }

    def to_audio_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        return {
            "type": "input_audio",
            "input_audio": {
                "data": mime_blob.raw_base64_str,
                "format": mime_blob.mime_type.split("/")[1],
            },
        }

    def to_video_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        return {
            "type": "video_url",
            "video_url": {
                "url": mime_blob.raw_base64_url,
            },
        }

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> dict[str, Any] | None:
        """
        NOTE: PDF Content must be placed second or later in the Content array.
        """
        return {
            "type": "input_file",
            "filename": display_name,
            "file_data": mime_blob.raw_base64_url,
        }

    # --------------------------------------------------
    # Template Methods (Lifecycle)
    # --------------------------------------------------

    async def _pre_request(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LangChainChatProviderContext:
        if self._should_use_responses_api(ctx.lc_messages):
            self.use_responses_api = True
            logger.debug("Using Responses API.")
        else:
            self.use_responses_api = False
            logger.debug("Using Chat Completions API.")

        return ctx

    async def _post_request(
        self,
        ctx: LangChainChatProviderContext,
        lc_ai_message: LCAIMessage,
    ) -> LCAIMessage:
        # NOTE: Remove reasoning content
        # When using Responses API with store=False,
        # remove it to prevent NotFoundError in the next request
        lc_ai_message = remove_content(lc_ai_message, "reasoning")
        lc_ai_message = normalize_content(lc_ai_message)
        return lc_ai_message

    # --------------------------------------------------
    # Template Methods (Invocation)
    # --------------------------------------------------

    async def _invoke(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LCAIMessage:
        lc_chat_model = self._create_lc_chat_model(ctx)

        additional_kwargs: dict[str, Any] = {}

        if self.use_responses_api:
            additional_kwargs["store"] = False
            additional_kwargs["max_output_tokens"] = self.settings.max_output_tokens

        return await lc_chat_model.ainvoke(ctx.lc_messages, **additional_kwargs)

    async def _stream(
        self,
        ctx: LangChainChatProviderContext,
    ) -> AsyncIterator[LCAIMessageChunk]:
        lc_chat_model = self._create_lc_chat_model(ctx)

        additional_kwargs: dict[str, Any] = {}

        if self.use_responses_api:
            additional_kwargs["store"] = False
            additional_kwargs["max_output_tokens"] = self.settings.max_output_tokens

        async for chunk in lc_chat_model.astream(ctx.lc_messages, **additional_kwargs):
            if isinstance(chunk, LCAIMessageChunk):
                yield chunk

    # --------------------------------------------------
    # Template Methods (Response Handling)
    # --------------------------------------------------

    def _extract_overflow_token_count(self, error: Exception) -> int | None:
        if "Your input exceeds the context window of this model" in str(error):
            return None

        if "Please reduce the length of the messages" in str(error):
            match = re.search(r"resulted in\s+(\d+)\s+tokens", str(error))
        else:
            match = None

        if not match:
            return None

        return int(match.group(1))

    def _get_cost_record(self, lc_ai_message: LCAIMessage) -> CostRecord | None:
        if not lc_ai_message.usage_metadata:
            return None

        input_token_details = lc_ai_message.usage_metadata.get(
            "input_token_details", {}
        )
        cached_input_tokens = input_token_details.get("cache_read", 0)
        input_tokens = lc_ai_message.usage_metadata.get("input_tokens", 0)
        input_tokens -= cached_input_tokens
        output_tokens = lc_ai_message.usage_metadata.get("output_tokens", 0)

        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        cached_input_cost = self.settings.cached_input_cost_microdollars_per_1k_tokens
        output_cost = self.settings.output_cost_microdollars_per_1k_tokens

        cost = math.ceil(
            input_cost * input_tokens / 1_000
            + cached_input_cost * cached_input_tokens / 1_000
            + output_cost * output_tokens / 1_000
        )

        return CostRecord(
            microdollars=cost,
            kind="chat",
            source=self.name,
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_input_tokens,
                "output_tokens": output_tokens,
            },
        )

    def _is_safety_error(self, lc_ai_message: LCAIMessage) -> bool:
        finish_reason = lc_ai_message.response_metadata.get("finish_reason")
        return finish_reason == "content_filter"

    def _is_max_token_error(self, lc_ai_message: LCAIMessage) -> bool:
        finish_reason = lc_ai_message.response_metadata.get("finish_reason")
        return finish_reason == "length"

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _create_lc_chat_model(
        self,
        ctx: LangChainChatProviderContext,
    ) -> BaseChatModel | Runnable[LanguageModelInput, LCAIMessage]:
        additional_params: dict[str, Any] = self.openai_settings.to_client_kwargs()

        if self.settings.reasoning_effort:
            additional_params["reasoning_effort"] = self.settings.reasoning_effort

        if self.settings.verbosity:
            additional_params["verbosity"] = self.settings.verbosity

        if self.settings.extra_body:
            additional_params["extra_body"] = self.settings.extra_body

        lc_chat_model = ChatOpenAI(
            model=self.settings.model_name,
            use_responses_api=self.use_responses_api,
            max_completion_tokens=self.settings.max_output_tokens,
            temperature=self.settings.temperature,
            tiktoken_model_name=self.settings.tiktoken_model_name,
            timeout=self.settings.timeout,
            **additional_params,
        )

        # Override get_token_ids to prevent errors when tokenizing text containing emojis
        def custom_get_token_ids(text: str) -> list[int]:
            _, encoding_model = lc_chat_model._get_encoding_model()

            return encoding_model.encode(
                text,
                allowed_special="all",
                disallowed_special=(),
            )

        lc_chat_model.custom_get_token_ids = custom_get_token_ids

        bind_kwargs: dict[str, Any] = {}

        parallel_tool_calls = ctx.parallel_tool_calls
        if parallel_tool_calls is None:
            parallel_tool_calls = self.settings.parallel_tool_calls

        if parallel_tool_calls is not None:
            bind_kwargs["parallel_tool_calls"] = parallel_tool_calls

        if ctx.lc_tool_infos:
            return lc_chat_model.bind_tools(
                cast(list[dict[str, Any]], ctx.lc_tool_infos),
                tool_choice=str(ctx.tool_choice or "auto"),
                **bind_kwargs,
            )

        else:
            return lc_chat_model

    def _should_use_responses_api(self, lc_messages: list[LCMessage]) -> bool:
        if self.settings.endpoint_type == "responses":
            return True

        return has_content(lc_messages, "input_file")
