from typing import Any

from .._models.yamnet_audio_tagging_provider import YamnetAudioTaggingProvider
from .._settings import YamnetAudioTaggingProviderSettings, settings_manager


def create_yamnet_audio_tagging_provider(**kwargs: Any) -> YamnetAudioTaggingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = YamnetAudioTaggingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return YamnetAudioTaggingProvider(settings)
