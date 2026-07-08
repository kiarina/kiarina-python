from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class CameraVideoSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_SOURCE_IMPL_CAMERA_",
        extra="ignore",
    )

    device: int | str = 0
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    """Requested camera FPS and maximum emitted FPS."""


settings_manager = SettingsManager(CameraVideoSourceSettings)
