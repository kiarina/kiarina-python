from typing import Any

from .._models.file_video_source import FileVideoSource
from .._settings import FileVideoSourceSettings, settings_manager


def create_file_video_source(**kwargs: Any) -> FileVideoSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = FileVideoSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return FileVideoSource(settings)
