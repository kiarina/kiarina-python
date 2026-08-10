import logging
from typing import Any, cast

from kiarina.agi.langchain_chat_provider import (
    LangChainChatProviderContext,
    LCAIMessage,
    LCContent,
    LCMessage,
    LCToolMessage,
)
from kiarina.utils.mime import MIMEBlob

from .._settings import LCAnthropicVertexChatProviderSettings

try:
    from langchain.chat_models import BaseChatModel
    from langchain_core.language_models import LanguageModelInput
    from langchain_core.runnables import Runnable
    from langchain_google_vertexai.model_garden import ChatAnthropicVertex

    import kiarina.lib.google
    from kiarina.agi.chat_provider_impl.lc_anthropic import (
        LCAnthropicChatProvider,
    )
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-google, langchain-anthropic, and "
        "langchain-google-vertexai are required to use "
        "LCAnthropicVertexChatProvider. "
        "Install them with: pip install "
        "'kiarina-agi-text[chat-provider-lc-anthropic-vertex]'"
    ) from exc

logger = logging.getLogger(__name__)


class LCAnthropicVertexChatProvider(LCAnthropicChatProvider):
    """
    LangChain Anthropic Vertex Chat Provider Implementation
    """

    def __init__(self, settings: LCAnthropicVertexChatProviderSettings) -> None:
        super().__init__(settings)

        self.settings: LCAnthropicVertexChatProviderSettings = settings

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def google_auth_settings(self) -> kiarina.lib.google.GoogleSettings:
        return kiarina.lib.google.settings_manager.get_settings(
            self.settings.google_auth_settings_key
        )

    @property
    def cloud_options(self) -> dict[str, Any]:
        return kiarina.lib.google.get_cloud_options(
            settings=self.google_auth_settings,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )

    # --------------------------------------------------
    # Methods (LangChainMediaConverter)
    # --------------------------------------------------

    def to_image_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        # NOTE: Use OpenAI format for image content
        # ChatAnthropicVertex does not support Anthropic format for image content
        return {
            "type": "image_url",
            "image_url": {
                "url": mime_blob.raw_base64_url,
                "detail": "high",
            },
        }

    # --------------------------------------------------
    # Template Methods (Lifecycle)
    # --------------------------------------------------

    async def _pre_request(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LangChainChatProviderContext:
        ctx = await super()._pre_request(ctx)

        lc_messages = _convert_image_content(ctx.lc_messages)
        return ctx.model_copy(lc_messages=lc_messages)

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _create_lc_chat_model(
        self,
        ctx: LangChainChatProviderContext,
    ) -> BaseChatModel | Runnable[LanguageModelInput, LCAIMessage]:
        lc_chat_model = ChatAnthropicVertex(
            location=self.settings.vertex_ai_location,
            model=self.settings.model_name,
            max_tokens=self.settings.max_output_tokens,
            temperature=self.settings.temperature,
            **self.cloud_options,
        )

        bind_kwargs: Any = {}

        parallel_tool_calls = ctx.parallel_tool_calls
        if parallel_tool_calls is None:
            parallel_tool_calls = self.settings.parallel_tool_calls

        if parallel_tool_calls is not None:
            bind_kwargs["disable_parallel_tool_use"] = not parallel_tool_calls

        if ctx.lc_tool_infos:
            return lc_chat_model.bind_tools(
                cast(list[dict[str, Any]], ctx.lc_tool_infos),
                tool_choice={
                    "type": str(ctx.tool_choice or "auto"),
                    **bind_kwargs,
                },
            )
        else:
            return lc_chat_model


# --------------------------------------------------
# Lifecycle Utility Functions
# --------------------------------------------------


def _convert_image_content(lc_messages: list[LCMessage]) -> list[LCMessage]:
    """
    Convert image content in ToolMessage from OpenAI format to Anthropic format.

    ChatAnthropicVertex does not convert image content in ToolMessage,
    so we need to convert it manually.
    """
    new_lc_messages: list[LCMessage] = []
    messages_converted = False

    for lc_message in lc_messages:
        if not isinstance(lc_message, LCToolMessage):
            new_lc_messages.append(lc_message)
        elif isinstance(lc_message.content, str):
            new_lc_messages.append(lc_message)
        else:
            new_content: list[str | LCContent] = []
            content_converted = False

            for content in lc_message.content:
                if isinstance(content, str):
                    new_content.append(content)
                elif not _is_target_content(content):
                    new_content.append(content)
                else:
                    url = content["image_url"].get("url") or ""

                    base64_data = url.split(",", 1)[1]
                    mime_type = url.split(";", 1)[0].split(":", 1)[1]

                    new_content.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": base64_data,
                            },
                        }
                    )

                    content_converted = True

            if not content_converted:
                new_lc_messages.append(lc_message)
            else:
                new_lc_messages.append(
                    lc_message.model_copy(update={"content": new_content})
                )
                messages_converted = True

    if not messages_converted:
        return lc_messages

    return new_lc_messages


def _is_target_content(lc_content: LCContent) -> bool:
    if lc_content.get("type") != "image_url":
        return False

    image_url_info = lc_content.get("image_url") or {}

    if not isinstance(image_url_info, dict) or not image_url_info:
        return False

    url = image_url_info.get("url")

    if not url or not isinstance(url, str):
        return False

    return url.startswith("data:image/")
