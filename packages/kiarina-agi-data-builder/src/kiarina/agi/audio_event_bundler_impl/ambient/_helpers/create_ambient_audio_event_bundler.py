from typing import Any

from .._models.ambient_audio_event_bundler import AmbientAudioEventBundler
from .._settings import AmbientAudioEventBundlerSettings, settings_manager


def create_ambient_audio_event_bundler(**kwargs: Any) -> AmbientAudioEventBundler:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = AmbientAudioEventBundlerSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return AmbientAudioEventBundler(settings)
