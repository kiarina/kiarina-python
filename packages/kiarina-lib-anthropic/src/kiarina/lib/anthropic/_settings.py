from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class AnthropicSettings(BaseSettings):
    """Anthropic client settings."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_ANTHROPIC_")

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="Anthropic API key.",
    )

    base_url: str | None = Field(
        default=None,
        title="Base URL",
        description="Base URL for the Anthropic API.",
    )


settings_manager = SettingsManager(AnthropicSettings, multi=True)
"""Manager for named Anthropic client settings."""
