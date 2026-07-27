from typing import Any

from .._models.video_file_info_builder import VideoFileInfoBuilder
from .._settings import VideoFileInfoBuilderSettings, settings_manager


def create_video_file_info_builder(**kwargs: Any) -> VideoFileInfoBuilder:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = VideoFileInfoBuilderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return VideoFileInfoBuilder(settings)
