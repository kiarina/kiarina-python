from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class NumpyVideoSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_SOURCE_IMPL_NUMPY_",
        extra="ignore",
    )

    fps: float = 30.0
    start_timestamp: float | None = None
    """Unix timestamp of the first frame; defaults to open() time."""


settings_manager = SettingsManager(NumpyVideoSourceSettings)
