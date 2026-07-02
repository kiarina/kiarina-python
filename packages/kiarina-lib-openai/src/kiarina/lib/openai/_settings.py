from typing import Any

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class OpenAISettings(BaseSettings):
    """OpenAI client settings."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_OPENAI_")

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="OpenAI API key.",
    )

    organization_id: str | None = Field(
        default=None,
        title="Organization ID",
        description="OpenAI organization ID.",
    )

    base_url: str | None = Field(
        default=None,
        title="Base URL",
        description="Base URL for the OpenAI API.",
    )

    def to_client_kwargs(self) -> dict[str, Any]:
        client_kwargs: dict[str, Any] = {}

        if self.api_key:
            client_kwargs["api_key"] = self.api_key.get_secret_value()

        if self.organization_id:
            client_kwargs["organization"] = self.organization_id

        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        return client_kwargs


settings_manager = SettingsManager(OpenAISettings, multi=True)
"""Manager for named OpenAI client settings."""
