from typing import Any

from .._models.stt_audio_event_bundler import STTAudioEventBundler
from .._settings import STTAudioEventBundlerSettings, settings_manager


def create_stt_audio_event_bundler(**kwargs: Any) -> STTAudioEventBundler:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = STTAudioEventBundlerSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return STTAudioEventBundler(settings)
