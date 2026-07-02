from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class CloudflareSettings(BaseSettings):
    """Cloudflare account settings."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_CLOUDFLARE_")

    account_id: str = Field(
        title="Account ID",
        description="Cloudflare account ID.",
    )

    api_token: SecretStr = Field(
        title="API Token",
        description="Cloudflare API token.",
    )


settings_manager = SettingsManager(CloudflareSettings, multi=True)
"""Manager for named Cloudflare account settings."""
