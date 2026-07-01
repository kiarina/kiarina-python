from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FileSettings(BaseSettings):
    """Settings for file locking."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_UTILS_FILE_")

    lock_dir: str | None = Field(
        default=None,
        title="Lock directory",
        description="Lock file directory. Uses the platform default when unset.",
    )

    lock_cleanup_enabled: bool = Field(
        default=True,
        title="Lock cleanup",
        description="Enable automatic cleanup of old lock files",
    )

    lock_max_age_hours: int = Field(
        default=24,
        ge=1,
        title="Maximum lock age",
        description="Maximum age for lock files in hours before cleanup",
    )


settings_manager = SettingsManager(FileSettings)
