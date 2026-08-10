from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.video_source_name import VideoSourceName


class VideoSourceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_SOURCE_",
        extra="ignore",
    )

    default: VideoSourceName = "camera"

    presets: dict[VideoSourceName, ImportPath] = Field(
        default_factory=lambda: {
            "camera": "kiarina.agi.video_source_impl.camera:create_camera_video_source",
            "file": "kiarina.agi.video_source_impl.file:create_file_video_source",
            "numpy": "kiarina.agi.video_source_impl.numpy:create_numpy_video_source",
            "queue": "kiarina.agi.video_source_impl.queue:create_queue_video_source",
        }
    )

    customs: dict[VideoSourceName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(VideoSourceSettings)
