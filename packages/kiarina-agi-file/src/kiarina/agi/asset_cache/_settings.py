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
        default=0,
        ge=0,
        title="Cache TTL",
        description="Maximum cache lifetime in seconds. Set to 0 for no expiration.",
    )


settings_manager = SettingsManager(AssetCacheSettings)
