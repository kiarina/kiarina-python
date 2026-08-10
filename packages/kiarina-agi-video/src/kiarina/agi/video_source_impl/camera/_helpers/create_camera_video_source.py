from typing import Any

from .._models.camera_video_source import CameraVideoSource
from .._settings import CameraVideoSourceSettings, settings_manager


def create_camera_video_source(**kwargs: Any) -> CameraVideoSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = CameraVideoSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return CameraVideoSource(settings)
