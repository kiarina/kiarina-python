from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.image_segmentation_provider_name import ImageSegmentationProviderName


class ImageSegmentationProviderSettings(BaseSettings):
    """Settings for image segmentation provider resolution."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_SEGMENTATION_PROVIDER_",
        extra="ignore",
    )

    presets: dict[ImageSegmentationProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.image_segmentation_provider_impl.mock:create_mock_image_segmentation_provider",
            "birefnet": "kiarina.agi.image_segmentation_provider_impl.birefnet:create_birefnet_image_segmentation_provider",
        },
        title="Provider Presets",
        description="Built-in image segmentation provider factories.",
    )
    customs: dict[ImageSegmentationProviderName, ImportPath] = Field(
        default_factory=dict,
        title="Custom Providers",
        description="User-defined image segmentation provider factories.",
    )


settings_manager = SettingsManager(ImageSegmentationProviderSettings)
