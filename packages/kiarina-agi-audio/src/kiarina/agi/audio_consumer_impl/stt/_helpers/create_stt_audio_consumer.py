from typing import Any

from .._models.stt_audio_consumer import STTAudioConsumer
from .._settings import STTAudioConsumerSettings, settings_manager


def create_stt_audio_consumer(**kwargs: Any) -> STTAudioConsumer:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = STTAudioConsumerSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return STTAudioConsumer(settings)
