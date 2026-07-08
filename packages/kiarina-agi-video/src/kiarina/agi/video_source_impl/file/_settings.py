from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FileVideoSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_SOURCE_IMPL_FILE_",
        extra="ignore",
    )

    fps: float | None = None
    """Frames per second to emit; defaults to the video file FPS."""
    start_timestamp: float | None = None
    """Unix timestamp of the first frame; defaults to open() time."""


settings_manager = SettingsManager(FileVideoSourceSettings)
