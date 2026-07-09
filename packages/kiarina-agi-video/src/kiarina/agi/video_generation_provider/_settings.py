from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.video_generation_provider_name import VideoGenerationProviderName


class VideoGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_GENERATION_PROVIDER_",
        extra="ignore",
    )

    presets: dict[VideoGenerationProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.video_generation_provider_impl.mock:create_mock_video_generation_provider",
            "google": "kiarina.agi.video_generation_provider_impl.google:create_google_video_generation_provider",
        }
    )

    customs: dict[VideoGenerationProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(VideoGenerationProviderSettings)
