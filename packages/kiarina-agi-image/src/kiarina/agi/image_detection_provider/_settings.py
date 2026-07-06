from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.image_detection_provider_name import ImageDetectionProviderName


class ImageDetectionProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_DETECTION_PROVIDER_",
        extra="ignore",
    )

    presets: dict[ImageDetectionProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.image_detection_provider_impl.mock:create_mock_image_detection_provider",
            "yunet": "kiarina.agi.image_detection_provider_impl.yunet:create_yunet_image_detection_provider",
            "dfine": "kiarina.agi.image_detection_provider_impl.dfine:create_dfine_image_detection_provider",
        }
    )

    customs: dict[ImageDetectionProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ImageDetectionProviderSettings)
