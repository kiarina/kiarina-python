from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.image_segmentation_model_config import ImageSegmentationModelConfig
from ._types.image_segmentation_model_alias import ImageSegmentationModelAlias
from ._types.image_segmentation_model_name import ImageSegmentationModelName
from ._types.image_segmentation_model_specifier import (
    ImageSegmentationModelSpecifier,
)


class ImageSegmentationModelSettings(BaseSettings):
    """Settings for image segmentation model resolution."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_SEGMENTATION_MODEL_",
        extra="ignore",
    )

    default: ImageSegmentationModelSpecifier = Field(
        default="birefnet",
        title="Default Model",
        description="Default image segmentation model specifier.",
    )
    aliases: dict[ImageSegmentationModelAlias, ImageSegmentationModelName] = Field(
        default_factory=lambda: {"remove-background": "birefnet"},
        title="Model Aliases",
        description="Aliases mapped to image segmentation model names.",
    )
    presets: dict[ImageSegmentationModelName, ImageSegmentationModelConfig] = Field(
        default_factory=lambda: {
            "mock": ImageSegmentationModelConfig(provider_name="mock"),
            "birefnet": ImageSegmentationModelConfig(provider_name="birefnet"),
        },
        title="Model Presets",
        description="Built-in image segmentation model configurations.",
    )
    customs: dict[ImageSegmentationModelName, ImageSegmentationModelConfig] = Field(
        default_factory=dict,
        title="Custom Models",
        description="User-defined image segmentation model configurations.",
    )


settings_manager = SettingsManager(ImageSegmentationModelSettings)
