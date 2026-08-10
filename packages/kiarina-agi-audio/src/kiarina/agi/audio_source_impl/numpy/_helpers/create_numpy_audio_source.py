from typing import Any

from .._models.numpy_audio_source import NumpyAudioSource
from .._settings import NumpyAudioSourceSettings, settings_manager


def create_numpy_audio_source(**kwargs: Any) -> NumpyAudioSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = NumpyAudioSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return NumpyAudioSource(settings)
