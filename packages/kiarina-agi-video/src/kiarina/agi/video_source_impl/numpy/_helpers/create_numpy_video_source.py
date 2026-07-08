from typing import Any

from .._models.numpy_video_source import NumpyVideoSource
from .._settings import NumpyVideoSourceSettings, settings_manager


def create_numpy_video_source(**kwargs: Any) -> NumpyVideoSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = NumpyVideoSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return NumpyVideoSource(settings)
