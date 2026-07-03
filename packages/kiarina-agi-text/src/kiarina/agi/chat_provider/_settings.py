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
            "lc_anthropic": "kiarina.agi.chat_provider_impl.lc_anthropic:create_lc_anthropic_chat_provider",
            "lc_anthropic_vertex": "kiarina.agi.chat_provider_impl.lc_anthropic_vertex:create_lc_anthropic_vertex_chat_provider",
            "lc_google": "kiarina.agi.chat_provider_impl.lc_google:create_lc_google_chat_provider",
            "lc_google_genai": "kiarina.agi.chat_provider_impl.lc_google_genai:create_lc_google_genai_chat_provider",
            "lc_openai": "kiarina.agi.chat_provider_impl.lc_openai:create_lc_openai_chat_provider",
            "mock": "kiarina.agi.chat_provider_impl.mock:create_mock_chat_provider",
        }
    )

    customs: dict[ChatProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ChatProviderSettings)
