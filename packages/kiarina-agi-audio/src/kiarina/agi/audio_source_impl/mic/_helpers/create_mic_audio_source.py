from typing import Any

from .._models.mic_audio_source import MicAudioSource
from .._settings import MicAudioSourceSettings, settings_manager


def create_mic_audio_source(**kwargs: Any) -> MicAudioSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MicAudioSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return MicAudioSource(settings)
