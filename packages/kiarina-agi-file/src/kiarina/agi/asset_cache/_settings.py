from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class AssetCacheSettings(BaseSettings):
    """Settings for the local asset cache."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASSET_CACHE_",
        extra="ignore",
    )

    hash_algorithm: str = Field(
        default="sha256",
        title="Hash Algorithm",
        description="Hash algorithm used to derive cache keys from asset URIs.",
    )
    cache_ttl: int = Field(
        default=86400,
        title="Cache TTL",
        description="Maximum cache lifetime in seconds.",
    )


settings_manager = SettingsManager(AssetCacheSettings)
