from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class GCSAssetRepositorySettings(BaseSettings):
    """Settings for Google Cloud Storage asset repositories."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASSET_REPOSITORY_IMPL_GCS_",
        extra="ignore",
    )

    google_auth_settings_key: str | None = Field(
        default=None,
        title="Google Authentication Settings Key",
        description="Key used to resolve Google authentication settings.",
    )


settings_manager = SettingsManager(GCSAssetRepositorySettings)
