from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class D1Settings(BaseSettings):
    """Cloudflare D1 database settings."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_CLOUDFLARE_D1_")

    database_id: str = Field(
        title="Database ID",
        description="Cloudflare D1 database ID.",
    )


settings_manager = SettingsManager(D1Settings, multi=True)
