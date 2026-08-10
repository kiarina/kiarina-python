from typing import Any

from .._models.queue_audio_source import QueueAudioSource
from .._settings import QueueAudioSourceSettings, settings_manager


def create_queue_audio_source(**kwargs: Any) -> QueueAudioSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = QueueAudioSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return QueueAudioSource(settings)
