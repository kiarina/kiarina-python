from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.chat_provider_name import ChatProviderName


class ChatProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_",
        extra="ignore",
    )

    presets: dict[ChatProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "anthropic": "kiarina.agi.chat_provider_impl.anthropic:create_anthropic_chat_provider",
            "anthropic_vertex": "kiarina.agi.chat_provider_impl.anthropic_vertex:create_anthropic_vertex_chat_provider",
            "claude_code": "kiarina.agi.chat_provider_impl.claude_code:create_claude_code_chat_provider",
            "codex": "kiarina.agi.chat_provider_impl.codex:create_codex_chat_provider",
            "google": "kiarina.agi.chat_provider_impl.google:create_google_chat_provider",
            "mock": "kiarina.agi.chat_provider_impl.mock:create_mock_chat_provider",
            "openai": "kiarina.agi.chat_provider_impl.openai:create_openai_chat_provider",
        }
    )

    customs: dict[ChatProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ChatProviderSettings)
