from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.aspect_ratio import AspectRatio
from ._types.image_size import ImageSize


class GoogleImageGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_GENERATION_PROVIDER_IMPL_GOOGLE_",
        extra="ignore",
    )

    google_auth_settings_key: SettingsKey | None = None

    model_name: str = "gemini-3-pro-image-preview"

    aspect_ratio: AspectRatio = "1:1"

    image_size: ImageSize | None = None

    input_cost_microdollars_per_1k_tokens: int = 2_000

    output_text_cost_microdollars_per_1k_tokens: int = 12_000

    output_image_cost_microdollars_per_1k_tokens: int = 120_000


settings_manager = SettingsManager(GoogleImageGenerationProviderSettings)
