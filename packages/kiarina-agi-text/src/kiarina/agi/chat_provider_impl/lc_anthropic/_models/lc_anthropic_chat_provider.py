import asyncio
import logging
import math
import re
from collections.abc import AsyncIterator
from typing import Any, cast

from kiarina.agi.chat_provider import ChatCapabilities, TokenOverflowError
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProvider,
    LangChainChatProviderContext,
    LCAIMessage,
    LCAIMessageChunk,
    LCBaseMessage,
    LCMessage,
    LCToolInfo,
    normalize_content,
    remove_content,
)
from kiarina.utils.mime import MIMEBlob

from .._settings import LCAnthropicChatProviderSettings
from .._types.cache_ttl import CacheTTL

try:
    from langchain.chat_models import BaseChatModel
    from langchain_anthropic import ChatAnthropic
    from langchain_anthropic.chat_models import convert_to_anthropic_tool
    from langchain_core.language_models import LanguageModelInput
    from langchain_core.runnables import Runnable
    from pydantic import SecretStr

    import kiarina.lib.anthropic
except ImportError as exc:
    raise ImportError(
        "anthropic and langchain-anthropic are required to use "
        "LCAnthropicChatProvider. "
        "Install them with: pip install 'kiarina-agi-text[chat-provider-lc-anthropic]'"
    ) from exc

logger = logging.getLogger(__name__)


class LCAnthropicChatProvider(LangChainChatProvider):
    """
    LangChain Anthropic Chat Provider Implementation
    """

    def __init__(self, settings: LCAnthropicChatProviderSettings) -> None:
        super().__init__()

        self.settings: LCAnthropicChatProviderSettings = settings

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
    def token_count_limit(self) -> int:
        return self.settings.token_count_limit

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
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_blob.mime_type,
                "data": mime_blob.raw_base64_str,
            },
        }

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> dict[str, Any] | None:
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": mime_blob.raw_base64_str,
            },
        }

    # --------------------------------------------------
    # Template Methods (Lifecycle)
    # --------------------------------------------------

    async def _pre_request(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LangChainChatProviderContext:
        lc_messages = _normalize_lc_messages(ctx.lc_messages)
        lc_tool_infos = _normalize_lc_tool_infos(ctx.lc_tool_infos)
        lc_tool_infos = _update_cache_ttl(lc_tool_infos, self.settings.cache_ttl)
        return ctx.model_copy(
            lc_messages=lc_messages,
            lc_tool_infos=lc_tool_infos,
        )

    async def _post_request(
        self,
        ctx: LangChainChatProviderContext,
        lc_ai_message: LCAIMessage,
    ) -> LCAIMessage:
        # If tool_calls exists, remove the tool_use content set simultaneously.
        lc_ai_message = remove_content(lc_ai_message, "tool_use")
        lc_ai_message = normalize_content(lc_ai_message)
        return lc_ai_message

    # --------------------------------------------------
    # Template Methods (Invocation)
    # --------------------------------------------------

    async def _invoke(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LCAIMessage:
        await self._check_token_overflow(ctx)

        lc_chat_model = self._create_lc_chat_model(ctx)

        for _ in range(self.settings.max_retry_count + 1):
            try:
                return await lc_chat_model.ainvoke(ctx.lc_messages)

            except Exception as error:
                if not _is_retryable_error(error):
                    raise

        raise RuntimeError("Max retry count exceeded.")

    async def _stream(
        self,
        ctx: LangChainChatProviderContext,
    ) -> AsyncIterator[LCAIMessageChunk]:
        await self._check_token_overflow(ctx)

        lc_chat_model = self._create_lc_chat_model(ctx)

        for _ in range(self.settings.max_retry_count + 1):
            try:
                async for chunk in lc_chat_model.astream(ctx.lc_messages):
                    if isinstance(chunk, LCAIMessageChunk):
                        yield chunk

                return

            except Exception as error:
                if not _is_retryable_error(error):
                    raise

        raise RuntimeError("Max retry count exceeded.")

    # --------------------------------------------------
    # Template Methods (Response Handling)
    # --------------------------------------------------

    def _extract_overflow_token_count(self, error: Exception) -> int | None:
        if "prompt is too long" in str(error):
            match = re.search(r"prompt is too long:\s*(\d+)\s*tokens", str(error))
        elif "exceed context limit" in str(error):
            match = re.search(r"context limit:\s*(\d+)\s*\+", str(error))
        elif "Token overflow error" in str(error):
            match = re.search(r"Token overflow error:\s*(\d+)\s*tokens", str(error))
        else:
            match = None

        if not match:
            return None

        return int(match.group(1))

    def _get_cost_record(self, lc_ai_message: LCAIMessage) -> CostRecord | None:
        if not lc_ai_message.usage_metadata:
            return None

        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        cache_write_5m_cost = (
            self.settings.cache_write_5m_cost_microdollars_per_1k_tokens
        )
        cache_write_1h_cost = (
            self.settings.cache_write_1h_cost_microdollars_per_1k_tokens
        )
        cached_input_cost = self.settings.cached_input_cost_microdollars_per_1k_tokens
        output_cost = self.settings.output_cost_microdollars_per_1k_tokens

        # Token details
        input_token_details = lc_ai_message.usage_metadata.get(
            "input_token_details", {}
        )

        cached_input_tokens = input_token_details.get("cache_read", 0)

        cache_write_5m_tokens = cast(
            int, input_token_details.get("ephemeral_5m_input_tokens", 0)
        )

        if self.settings.cache_ttl == "5m" and cache_write_5m_tokens == 0:
            cache_write_5m_tokens = input_token_details.get("cache_creation", 0)

        cache_write_1h_tokens = cast(
            int, input_token_details.get("ephemeral_1h_input_tokens", 0)
        )

        if self.settings.cache_ttl == "1h" and cache_write_1h_tokens == 0:
            cache_write_1h_tokens = input_token_details.get("cache_creation", 0)

        input_tokens = (
            lc_ai_message.usage_metadata.get("input_tokens", 0)
            - cached_input_tokens
            - cache_write_5m_tokens
            - cache_write_1h_tokens
        )

        output_tokens = lc_ai_message.usage_metadata.get("output_tokens", 0)

        # Context 1M multipliers
        multiplier_input = 1.0
        multiplier_output = 1.0

        if (
            self.settings.context_1m_enabled
            and input_tokens >= self.settings.context_1m_threshold_tokens
        ):
            multiplier_input = self.settings.context_1m_input_cost_multiplier
            multiplier_output = self.settings.context_1m_output_cost_multiplier

        # Cost calculation
        # fmt: off
        cost = math.ceil(
            input_cost * multiplier_input * input_tokens / 1_000
            + cache_write_5m_cost * multiplier_input * cache_write_5m_tokens / 1_000
            + cache_write_1h_cost * multiplier_input * cache_write_1h_tokens / 1_000
            + cached_input_cost * multiplier_input * cached_input_tokens / 1_000
            + output_cost * multiplier_output * output_tokens / 1_000
        )
        # fmt: on

        return CostRecord(
            microdollars=cost,
            kind="chat",
            source=self.name,
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "cache_write_5m_tokens": cache_write_5m_tokens,
                "cache_write_1h_tokens": cache_write_1h_tokens,
                "cached_input_tokens": cached_input_tokens,
                "output_tokens": output_tokens,
            },
        )

    def _is_safety_error(self, lc_ai_message: LCAIMessage) -> bool:
        finish_reason = lc_ai_message.response_metadata.get("stop_reason")
        return finish_reason == "safety"

    def _is_max_token_error(self, lc_ai_message: LCAIMessage) -> bool:
        finish_reason = lc_ai_message.response_metadata.get("stop_reason")
        return finish_reason == "max_tokens"

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _create_lc_chat_model(
        self,
        ctx: LangChainChatProviderContext,
    ) -> BaseChatModel | Runnable[LanguageModelInput, LCAIMessage]:
        additional_params: dict[str, Any] = {}

        if self.anthropic_settings.api_key is not None:
            additional_params["api_key"] = self.anthropic_settings.api_key

        if self.settings.context_1m_enabled:
            additional_params["betas"] = ["context-1m-2025-08-07"]

        lc_chat_model = ChatAnthropic(
            model_name=self.settings.model_name,
            max_tokens_to_sample=self.settings.max_output_tokens,
            temperature=self.settings.temperature,
            timeout=self.settings.timeout,
            stop=None,
            **additional_params,
        )

        bind_kwargs: dict[str, Any] = {}

        parallel_tool_calls = ctx.parallel_tool_calls
        if parallel_tool_calls is None:
            parallel_tool_calls = self.settings.parallel_tool_calls

        if parallel_tool_calls is not None:
            bind_kwargs["parallel_tool_calls"] = parallel_tool_calls

        if ctx.lc_tool_infos:
            return lc_chat_model.bind_tools(
                ctx.lc_tool_infos,
                tool_choice=ctx.tool_choice or "auto",
                **bind_kwargs,
            )
        else:
            return lc_chat_model

    async def _check_token_overflow(
        self,
        ctx: LangChainChatProviderContext,
    ) -> None:
        try:
            token_count = await _get_num_tokens(
                ctx.lc_messages,
                ctx.lc_tool_infos,
                self.token_count_model_name,
                self.anthropic_settings.api_key,
            )

            if token_count > self.token_count_limit:
                raise TokenOverflowError(token_count)

        except TokenOverflowError:
            raise

        except Exception:
            # NOTE: Ignore errors and attempt API request
            pass


# --------------------------------------------------
# Life Cycle Utility Functions
# --------------------------------------------------


def _normalize_lc_messages(lc_messages: list[LCMessage]) -> list[LCMessage]:
    """
    Normalize messages

    NOTE: Set dummy text for empty content
    - To prevent errors in _format_params of _astream
    """
    new_lc_messages: list[LCMessage] = []
    changed = False

    for lc_message in lc_messages:
        if new_lc_message := _normalize_lc_message(lc_message):
            new_lc_messages.append(new_lc_message)
            changed = True
        else:
            new_lc_messages.append(lc_message)

    if not changed:
        return lc_messages

    return new_lc_messages


def _normalize_lc_message(lc_message: LCMessage) -> LCMessage | None:
    if isinstance(lc_message.content, str):
        if not lc_message.content.strip():
            return lc_message.model_copy(update={"content": "<no message>"})

        return None

    if not len(lc_message.content):
        return lc_message.model_copy(update={"content": "<no message>"})

    # Remove unavailable contents
    filtered_lc_message = remove_content(lc_message, "function_call")

    if filtered_lc_message is lc_message:
        return None

    if not len(filtered_lc_message.content):
        return filtered_lc_message.model_copy(update={"content": "<no message>"})
    else:
        return filtered_lc_message


def _normalize_lc_tool_infos(
    lc_tool_infos: list[LCToolInfo] | None,
) -> list[LCToolInfo] | None:
    if not lc_tool_infos:
        return lc_tool_infos

    anthropic_lc_tool_infos: list[LCToolInfo] = []

    for lc_tool_info in lc_tool_infos:
        if "parameters" not in lc_tool_info:
            lc_tool_info = {
                **lc_tool_info,
                "parameters": {"type": "object", "properties": {}},
            }

        anthropic_tool = convert_to_anthropic_tool(lc_tool_info)

        if "cache_control" in lc_tool_info:
            anthropic_tool["cache_control"] = lc_tool_info["cache_control"]

        anthropic_lc_tool_infos.append(cast(LCToolInfo, anthropic_tool))

    return anthropic_lc_tool_infos


def _update_cache_ttl(
    lc_tool_infos: list[LCToolInfo] | None,
    cache_ttl: CacheTTL,
) -> list[LCToolInfo] | None:
    if not lc_tool_infos:
        return lc_tool_infos

    if cache_ttl == "5m":
        return lc_tool_infos

    new_lc_tool_infos: list[LCToolInfo] = []
    updated = False

    for lc_tool_info in lc_tool_infos:
        if "cache_control" in lc_tool_info:
            new_lc_tool_info = lc_tool_info.copy()
            new_lc_tool_info["cache_control"] = {"type": "ephemeral", "ttl": "1h"}
            new_lc_tool_infos.append(new_lc_tool_info)
            updated = True
        else:
            new_lc_tool_infos.append(lc_tool_info)

    if updated:
        return new_lc_tool_infos
    else:
        return lc_tool_infos


# --------------------------------------------------
# Invocation Utility Functions
# --------------------------------------------------


async def _get_num_tokens(
    lc_messages: list[LCMessage],
    lc_tool_infos: list[LCToolInfo] | None,
    model_name: str,
    api_key: SecretStr | None,
) -> int:
    additional_params: dict[str, Any] = {}

    if api_key is not None:
        additional_params["api_key"] = api_key.get_secret_value()

    chat_anthropic = ChatAnthropic(
        model_name=model_name,
        **additional_params,
    )

    lc_base_messages = [cast(LCBaseMessage, m) for m in lc_messages]
    lc_tool_infos = lc_tool_infos or []

    return await asyncio.to_thread(
        chat_anthropic.get_num_tokens_from_messages,
        lc_base_messages,
        cast(list[dict[str, Any]], lc_tool_infos),
    )


def _is_retryable_error(error: Exception) -> bool:
    if "Overload" in str(error):
        return True

    if "429" in str(error):
        return True

    return False
