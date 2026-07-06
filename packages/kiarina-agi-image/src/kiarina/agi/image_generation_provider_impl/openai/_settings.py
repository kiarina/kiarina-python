from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.background import Background
from ._types.output_format import OutputFormat
from ._types.quality import Quality
from ._types.size import Size


class OpenAIImageGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_GENERATION_PROVIDER_IMPL_OPENAI_",
        extra="ignore",
    )

    openai_settings_key: SettingsKey | None = None

    model_name: str = "gpt-image-1.5"

    background: Background = "opaque"

    output_format: OutputFormat = "jpeg"

    quality: Quality = "auto"

    size: Size = "1024x1024"

    mask_file_path: str | None = None

    base_file_paths: list[str] = Field(default_factory=list)

    timeout: float = 120.0

    input_text_cost_microdollars_per_1k_tokens: int = 5_000

    input_image_cost_microdollars_per_1k_tokens: int = 8_000

    output_image_cost_microdollars_per_1k_tokens: int = 32_000


settings_manager = SettingsManager(OpenAIImageGenerationProviderSettings)
