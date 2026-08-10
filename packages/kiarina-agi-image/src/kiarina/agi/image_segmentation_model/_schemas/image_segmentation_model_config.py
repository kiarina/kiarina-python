from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.image_segmentation_provider import ImageSegmentationProviderName


class ImageSegmentationModelConfig(BaseModel):
    """Configuration for an image segmentation model."""

    provider_name: ImageSegmentationProviderName = Field(
        title="Provider Name",
        description="Name of the image segmentation provider.",
    )
    provider_config: dict[str, Any] = Field(
        default_factory=dict,
        title="Provider Configuration",
        description="Configuration overrides passed to the provider.",
    )
    visible: bool = Field(
        default=True,
        title="Visible",
        description="Whether the model is visible to model selectors.",
    )
