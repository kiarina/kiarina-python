from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.aspect_ratio import AspectRatio
from ._types.duration_seconds import DurationSeconds
from ._types.model_name import ModelName
from ._types.resolution import Resolution


class GoogleVideoGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_GENERATION_PROVIDER_IMPL_GOOGLE_",
        extra="ignore",
    )

    google_auth_settings_key: SettingsKey | None = None

    model_name: ModelName = "veo-3.1-generate-preview"

    aspect_ratio: AspectRatio = "16:9"

    resolution: Resolution = "720p"

    duration_seconds: DurationSeconds = "8"

    negative_prompt: str = ""

    reference_images: list[str] = Field(default_factory=list)
    """List of images to use as style and content references. Up to 3 images can be specified."""

    last_image_file_path: str | None = None

    timeout_milliseconds: int = 3_600_000

    cost_microdollars_per_second: int = 400_000  # $0.40/sec


settings_manager = SettingsManager(GoogleVideoGenerationProviderSettings)
