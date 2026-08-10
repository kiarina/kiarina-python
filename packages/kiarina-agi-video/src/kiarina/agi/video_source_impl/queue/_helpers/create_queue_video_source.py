from typing import Any

from .._models.queue_video_source import QueueVideoSource
from .._settings import QueueVideoSourceSettings, settings_manager


def create_queue_video_source(**kwargs: Any) -> QueueVideoSource:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = QueueVideoSourceSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return QueueVideoSource(settings)
