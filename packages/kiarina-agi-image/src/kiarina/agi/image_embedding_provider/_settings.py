from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.image_embedding_provider_name import ImageEmbeddingProviderName


class ImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_",
        extra="ignore",
    )

    presets: dict[ImageEmbeddingProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.image_embedding_provider_impl.mock:create_mock_image_embedding_provider",
            "gemini": "kiarina.agi.image_embedding_provider_impl.gemini:create_gemini_image_embedding_provider",
            "qwen3-vl": "kiarina.agi.image_embedding_provider_impl.qwen3_vl:create_qwen3_vl_image_embedding_provider",
            "siglip2": "kiarina.agi.image_embedding_provider_impl.siglip2:create_siglip2_image_embedding_provider",
            "sface": "kiarina.agi.image_embedding_provider_impl.sface:create_sface_image_embedding_provider",
        }
    )

    customs: dict[ImageEmbeddingProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ImageEmbeddingProviderSettings)
