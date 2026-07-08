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

    default: VideoGenerationModelSpecifier = "openai"

    aliases: dict[VideoGenerationModelAlias, VideoGenerationModelName] = Field(
        default_factory=lambda: {
            "openai": "sora-2",
            "google": "veo-3.1",
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
            # openai
            # --------------------------------------------------
            "sora-2-pro": VideoGenerationModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "sora-2-pro",
                    "cost_microdollars_720p_per_second": 300_000,
                    "cost_microdollars_1024p_per_second": 500_000,
                },
                capabilities=VideoGenerationCapabilities(
                    edit_enabled=True,
                    extend_enabled=False,
                ),
            ),
            "sora-2": VideoGenerationModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "sora-2",
                    "cost_microdollars_720p_per_second": 100_000,
                },
                capabilities=VideoGenerationCapabilities(
                    edit_enabled=True,
                    extend_enabled=False,
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
        },
    )

    customs: dict[VideoGenerationModelName, VideoGenerationModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(VideoGenerationModelSettings)
