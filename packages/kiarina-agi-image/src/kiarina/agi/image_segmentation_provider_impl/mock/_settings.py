from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockImageSegmentationProviderSettings(BaseSettings):
    """Settings for the mock image segmentation provider."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_SEGMENTATION_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    mask_value: Literal[0, 255] = Field(
        default=255,
        title="Mask Value",
        description="Value used to fill the binary segmentation mask.",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        title="Confidence",
        description="Optional value used to fill the confidence map.",
    )


settings_manager = SettingsManager(MockImageSegmentationProviderSettings)
