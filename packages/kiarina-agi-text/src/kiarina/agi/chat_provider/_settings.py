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
            "google_genai": "kiarina.agi.chat_provider_impl.google_genai:create_google_genai_chat_provider",
            "mock": "kiarina.agi.chat_provider_impl.mock:create_mock_chat_provider",
            "openai": "kiarina.agi.chat_provider_impl.openai:create_openai_chat_provider",
        }
    )

    customs: dict[ChatProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ChatProviderSettings)
