from pydantic_settings import SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from kiarina.agi.chat_provider_impl.lc_anthropic import (
    LCAnthropicChatProviderSettings,
)


class LCAnthropicVertexChatProviderSettings(LCAnthropicChatProviderSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_LC_ANTHROPIC_VERTEX_",
        extra="ignore",
    )

    model_name: str = "claude-haiku-4-5@20251001"

    token_count_model_name: str = "claude-haiku-4-5"

    google_auth_settings_key: SettingsKey | None = None

    vertex_ai_location: str = "us-east5"


settings_manager = SettingsManager(LCAnthropicVertexChatProviderSettings)
