from typing import Any

from .._models.file_audio_source import FileAudioSource
from .._settings import FileAudioSourceSettings, settings_manager


def create_file_audio_source(**kwargs: Any) -> FileAudioSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = FileAudioSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return FileAudioSource(settings)
