from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.video_generation_capabilities import VideoGenerationCapabilities
from ._schemas.video_generation_model_config import VideoGenerationModelConfig
from ._types.video_generation_model_alias import VideoGenerationModelAlias
from ._types.video_generation_model_name import VideoGenerationModelName
from ._types.video_generation_model_specifier import VideoGenerationModelSpecifier


class VideoGenerationModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_GENERATION_MODEL_",
        extra="ignore",
    )

    default: VideoGenerationModelSpecifier = "google"

    aliases: dict[VideoGenerationModelAlias, VideoGenerationModelName] = Field(
        default_factory=lambda: {
            "google": "veo-3.1",
            "kiapi": "kiapi-video",
        }
    )

    presets: dict[VideoGenerationModelName, VideoGenerationModelConfig] = Field(
        default_factory=lambda: {
            # --------------------------------------------------
            # mock
            # --------------------------------------------------
            "mock": VideoGenerationModelConfig(
                provider_name="mock",
                capabilities=VideoGenerationCapabilities(
                    edit_enabled=True,
                    extend_enabled=True,
                ),
            ),
            # --------------------------------------------------
            # google
            # --------------------------------------------------
            "veo-3.1": VideoGenerationModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "veo-3.1-generate-preview",
                    "cost_microdollars_per_second": 400_000,
                },
                capabilities=VideoGenerationCapabilities(
                    edit_enabled=False,
                    extend_enabled=True,
                ),
            ),
            "veo-3.1-fast": VideoGenerationModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "veo-3.1-fast-generate-preview",
                    "cost_microdollars_per_second": 150_000,
                },
                capabilities=VideoGenerationCapabilities(
                    edit_enabled=False,
                    extend_enabled=True,
                ),
            ),
            # --------------------------------------------------
            # kiapi
            # --------------------------------------------------
            "kiapi-video": VideoGenerationModelConfig(
                provider_name="kiapi",
            ),
        },
    )

    customs: dict[VideoGenerationModelName, VideoGenerationModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(VideoGenerationModelSettings)
