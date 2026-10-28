from pydantic_settings import SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from kiarina.agi.chat_provider_impl.anthropic import (
    AnthropicChatProviderSettings,
)


class AnthropicVertexChatProviderSettings(AnthropicChatProviderSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_ANTHROPIC_VERTEX_",
        extra="ignore",
    )

    model_name: str = "claude-haiku-5-5"

    token_count_model_name: str | None = None

    google_auth_settings_key: SettingsKey | None = None

    vertex_ai_location: str = "global"


settings_manager = SettingsManager(AnthropicVertexChatProviderSettings)
