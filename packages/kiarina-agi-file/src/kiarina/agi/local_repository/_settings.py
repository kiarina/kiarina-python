from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.file_path_policy import FilePathPolicy


class LocalRepositorySettings(BaseSettings):
    """Settings for local file repositories."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_LOCAL_REPOSITORY_",
        extra="ignore",
    )

    file_path_policy: FilePathPolicy = Field(
        default_factory=FilePathPolicy,
        title="File Path Policy",
        description="Rules and templates used for local file paths.",
    )


settings_manager = SettingsManager(LocalRepositorySettings)
