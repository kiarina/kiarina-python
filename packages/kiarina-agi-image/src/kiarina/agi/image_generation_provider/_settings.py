from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.image_generation_provider_name import ImageGenerationProviderName


class ImageGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_GENERATION_PROVIDER_",
        extra="ignore",
    )

    presets: dict[ImageGenerationProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.image_generation_provider_impl.mock:create_mock_image_generation_provider",
            "openai": "kiarina.agi.image_generation_provider_impl.openai:create_openai_image_generation_provider",
            "google": "kiarina.agi.image_generation_provider_impl.google:create_google_image_generation_provider",
        }
    )

    customs: dict[ImageGenerationProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ImageGenerationProviderSettings)
