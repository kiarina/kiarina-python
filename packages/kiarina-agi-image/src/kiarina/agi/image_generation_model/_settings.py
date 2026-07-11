from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.image_generation_model_config import ImageGenerationModelConfig
from ._types.image_generation_model_alias import ImageGenerationModelAlias
from ._types.image_generation_model_name import ImageGenerationModelName
from ._types.image_generation_model_specifier import ImageGenerationModelSpecifier


class ImageGenerationModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_GENERATION_MODEL_",
        extra="ignore",
    )

    default: ImageGenerationModelSpecifier = "openai"

    aliases: dict[ImageGenerationModelAlias, ImageGenerationModelName] = Field(
        default_factory=lambda: {
            "openai": "gpt-image-1.5",
            "google": "gemini-3.1-flash-image-preview",
            "kiapi": "kiapi-image",
        }
    )

    presets: dict[ImageGenerationModelName, ImageGenerationModelConfig] = Field(
        default_factory=lambda: {
            # --------------------------------------------------
            # mock
            # --------------------------------------------------
            "mock": ImageGenerationModelConfig(
                provider_name="mock",
            ),
            # --------------------------------------------------
            # openai
            # --------------------------------------------------
            "gpt-image-1.5": ImageGenerationModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "gpt-image-1.5",
                    "input_text_cost_microdollars_per_1k_tokens": 5_000,
                    "input_image_cost_microdollars_per_1k_tokens": 8_000,
                    "output_image_cost_microdollars_per_1k_tokens": 32_000,
                },
            ),
            "gpt-image-1-mini": ImageGenerationModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "gpt-image-1-mini",
                    "input_text_cost_microdollars_per_1k_tokens": 2_000,
                    "input_image_cost_microdollars_per_1k_tokens": 2_500,
                    "output_image_cost_microdollars_per_1k_tokens": 8_000,
                },
            ),
            # --------------------------------------------------
            # google
            # --------------------------------------------------
            "gemini-3.1-flash-image-preview": ImageGenerationModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "gemini-3.1-flash-image-preview",
                    "input_cost_microdollars_per_1k_tokens": 500,
                    "output_image_cost_microdollars_per_1k_tokens": 30_000,
                },
            ),
            "gemini-3-pro-image-preview": ImageGenerationModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "gemini-3-pro-image-preview",
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "output_text_cost_microdollars_per_1k_tokens": 12_000,
                    "output_image_cost_microdollars_per_1k_tokens": 120_000,
                },
            ),
            # --------------------------------------------------
            # kiapi
            # --------------------------------------------------
            "kiapi-image": ImageGenerationModelConfig(
                provider_name="kiapi",
            ),
        }
    )

    customs: dict[ImageGenerationModelName, ImageGenerationModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(ImageGenerationModelSettings)
