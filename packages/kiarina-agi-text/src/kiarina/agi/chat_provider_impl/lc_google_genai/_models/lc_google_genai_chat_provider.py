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
    normalize_content,
)
from kiarina.utils.mime import MIMEBlob

from .._settings import LCGoogleGenAIChatProviderSettings

try:
    from langchain.chat_models import BaseChatModel
    from langchain_core.language_models import LanguageModelInput
    from langchain_core.runnables import Runnable
    from langchain_core.utils.function_calling import convert_to_openai_tool
    from langchain_google_genai import ChatGoogleGenerativeAI

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "google-genai, kiarina-lib-google, and langchain-google-genai are "
        "required to use LCGoogleGenAIChatProvider. "
        "Install them with: pip install 'kiarina-agi-text[chat-provider-lc-google-genai]'"
    ) from exc

logger = logging.getLogger(__name__)


class LCGoogleGenAIChatProvider(LangChainChatProvider):
    """
    LangChain Google Generative AI Chat Provider Implementation
    """

    def __init__(self, settings: LCGoogleGenAIChatProviderSettings) -> None:
        super().__init__()

        self.settings: LCGoogleGenAIChatProviderSettings = settings

    def __str__(self) -> str:
        props: list[str] = [
            self.settings.model_name,
            self.settings.backend_type,
        ]

        return f"{self.__class__.__name__}({', '.join(props)})"

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def google_auth_settings(self) -> kiarina.lib.google.GoogleSettings:
        return kiarina.lib.google.settings_manager.get_settings(
            self.settings.google_auth_settings_key
        )

    @property
    def credentials(self) -> kiarina.lib.google.Credentials:
        credentials = kiarina.lib.google.get_credentials(
            settings=self.google_auth_settings,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )

        return credentials

    @property
    def backend_config(self) -> dict[str, Any]:
        backend_config: dict[str, Any] = {}

        if self.settings.backend_type == "gemini_api":
            if self.google_auth_settings.api_key is not None:
                backend_config = {
                    "api_key": self.google_auth_settings.api_key,
                }

            return backend_config

        elif self.settings.backend_type == "vertex_ai_api_key":
            backend_config = {
                "api_key": self.google_auth_settings.api_key,
                "project": self.google_auth_settings.project_id,
                "vertexai": True,
            }

            if self.settings.vertex_ai_location:
                backend_config["location"] = self.settings.vertex_ai_location

            return backend_config

        else:
            backend_config = {
                "credentials": self.credentials,
                "project": self.google_auth_settings.project_id,
            }

            if self.settings.vertex_ai_location:
                backend_config["location"] = self.settings.vertex_ai_location

            return backend_config

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
            "type": "media",
            "mime_type": mime_blob.mime_type,
            "data": mime_blob.raw_data,
        }

    def to_video_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        return {
            "type": "media",
            "mime_type": mime_blob.mime_type,
            "data": mime_blob.raw_data,
        }

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> dict[str, Any] | None:
        return {
            "type": "media",
            "mime_type": "application/pdf",
            "data": mime_blob.raw_data,
        }

    # --------------------------------------------------
    # Template Methods (Lifecycle)
    # --------------------------------------------------

    async def _post_request(
        self,
        ctx: LangChainChatProviderContext,
        lc_ai_message: LCAIMessage,
    ) -> LCAIMessage:
        lc_ai_message = normalize_content(lc_ai_message)

        parallel_tool_calls = ctx.parallel_tool_calls
        if parallel_tool_calls is None:
            parallel_tool_calls = self.settings.parallel_tool_calls

        if parallel_tool_calls is False and len(lc_ai_message.tool_calls) > 1:
            lc_ai_message = lc_ai_message.model_copy(
                update={"tool_calls": [lc_ai_message.tool_calls[0]]}
            )

        return lc_ai_message

    # --------------------------------------------------
    # Template Methods (Invocation)
    # --------------------------------------------------

    async def _invoke(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LCAIMessage:
        lc_chat_model = self._create_lc_chat_model(ctx)
        return await lc_chat_model.ainvoke(ctx.lc_messages)

    async def _stream(
        self,
        ctx: LangChainChatProviderContext,
    ) -> AsyncIterator[LCAIMessageChunk]:
        lc_chat_model = self._create_lc_chat_model(ctx)

        async for chunk in lc_chat_model.astream(ctx.lc_messages):
            if isinstance(chunk, LCAIMessageChunk):
                yield chunk

    # --------------------------------------------------
    # Template Methods (Response Handling)
    # --------------------------------------------------

    def _extract_overflow_token_count(self, error: Exception) -> int | None:
        if (
            "The input token count exceeds the maximum number of tokens allowed"
            not in str(error)
        ):
            return None

        match = re.search(r"allowed (\d+)", str(error))

        if not match:
            return None

        return int(match.group(1))

    def _get_cost_record(self, lc_ai_message: LCAIMessage) -> CostRecord | None:
        if not lc_ai_message.usage_metadata:
            return None

        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        extended_input_cost = (
            self.settings.extended_input_cost_microdollars_per_1k_tokens
        )
        cached_input_cost = self.settings.cached_input_cost_microdollars_per_1k_tokens
        extended_cached_input_cost = (
            self.settings.extended_cached_input_cost_microdollars_per_1k_tokens
        )
        output_cost = self.settings.output_cost_microdollars_per_1k_tokens
        extended_output_cost = (
            self.settings.extended_output_cost_microdollars_per_1k_tokens
        )

        input_token_details = lc_ai_message.usage_metadata.get(
            "input_token_details", {}
        )
        cached_input_tokens = input_token_details.get("cache_read", 0)
        prompt_tokens = lc_ai_message.usage_metadata.get("input_tokens", 0)
        input_tokens = prompt_tokens - cached_input_tokens
        output_tokens = lc_ai_message.usage_metadata.get("output_tokens", 0)

        if prompt_tokens <= self.settings.threshold_tokens:
            cost = math.ceil(
                input_cost * input_tokens / 1_000
                + cached_input_cost * cached_input_tokens / 1_000
                + output_cost * output_tokens / 1_000
            )
        else:
            cost = math.ceil(
                extended_input_cost * input_tokens / 1_000
                + extended_cached_input_cost * cached_input_tokens / 1_000
                + extended_output_cost * output_tokens / 1_000
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
        finish_reason = str(lc_ai_message.response_metadata.get("finish_reason", ""))
        return "safety" in finish_reason.lower()

    def _is_max_token_error(self, lc_ai_message: LCAIMessage) -> bool:
        finish_reason = str(lc_ai_message.response_metadata.get("finish_reason", ""))

        if "max_tokens" in finish_reason.lower():
            return True

        # Check if output tokens reached the limit
        if lc_ai_message.usage_metadata:
            output_tokens = lc_ai_message.usage_metadata.get("output_tokens", 0)

            if output_tokens >= self.settings.max_output_tokens:
                return True

        return False

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _create_lc_chat_model(
        self,
        ctx: LangChainChatProviderContext,
    ) -> BaseChatModel | Runnable[LanguageModelInput, LCAIMessage]:
        lc_chat_model = ChatGoogleGenerativeAI(
            **self.backend_config,
            model=self.settings.model_name,
            max_tokens=self.settings.max_output_tokens,
            temperature=self.settings.temperature,
        )

        if ctx.lc_tool_infos:
            if len(ctx.lc_tool_infos) == 1 and ctx.tool_choice == "any":
                schema = convert_to_openai_tool(ctx.lc_tool_infos[0])

                return lc_chat_model.bind_tools(
                    cast(list[dict[str, Any]], ctx.lc_tool_infos),
                    tool_choice=schema["function"]["name"],
                    ls_structured_output_format={
                        "kwargs": {"method": "function_calling"},
                        "schema": schema,
                    },
                )

            else:
                return lc_chat_model.bind_tools(
                    cast(list[dict[str, Any]], ctx.lc_tool_infos),
                    tool_choice=str(ctx.tool_choice or "auto"),
                )

        else:
            return lc_chat_model
