from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.image_embedding_model_config import ImageEmbeddingModelConfig
from ._types.image_embedding_model_alias import ImageEmbeddingModelAlias
from ._types.image_embedding_model_name import ImageEmbeddingModelName
from ._types.image_embedding_model_specifier import ImageEmbeddingModelSpecifier


class ImageEmbeddingModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_MODEL_",
        extra="ignore",
    )

    default: ImageEmbeddingModelSpecifier = "mock"

    aliases: dict[ImageEmbeddingModelAlias, ImageEmbeddingModelName] = Field(
        default_factory=lambda: {
            "seen": "qwen3-vl",
            "object": "siglip2",
            "face": "sface",
        }
    )

    presets: dict[ImageEmbeddingModelName, ImageEmbeddingModelConfig] = Field(
        default_factory=lambda: {
            "mock": ImageEmbeddingModelConfig(provider_name="mock"),
            "gemini": ImageEmbeddingModelConfig(provider_name="gemini"),
            "qwen3-vl": ImageEmbeddingModelConfig(provider_name="qwen3-vl"),
            "siglip2": ImageEmbeddingModelConfig(
                provider_name="siglip2",
                provider_config={
                    "model_path": "models/siglip2/vision_model_int8.onnx",
                },
            ),
            "sface": ImageEmbeddingModelConfig(
                provider_name="sface",
                provider_config={
                    "model_path": "models/sface/face_recognition_sface_2021dec.onnx",
                },
            ),
        }
    )

    customs: dict[ImageEmbeddingModelName, ImageEmbeddingModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(ImageEmbeddingModelSettings)
