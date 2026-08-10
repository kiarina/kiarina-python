from typing import Any

from .._models.ambient_audio_consumer import AmbientAudioConsumer
from .._settings import AmbientAudioConsumerSettings, settings_manager


def create_ambient_audio_consumer(**kwargs: Any) -> AmbientAudioConsumer:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = AmbientAudioConsumerSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return AmbientAudioConsumer(settings)
