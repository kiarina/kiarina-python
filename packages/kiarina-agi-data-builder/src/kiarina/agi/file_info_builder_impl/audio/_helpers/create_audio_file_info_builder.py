from typing import Any

from .._models.audio_file_info_builder import AudioFileInfoBuilder
from .._settings import AudioFileInfoBuilderSettings, settings_manager


def create_audio_file_info_builder(**kwargs: Any) -> AudioFileInfoBuilder:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = AudioFileInfoBuilderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return AudioFileInfoBuilder(settings)
