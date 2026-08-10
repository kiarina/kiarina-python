from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.image_detection_model_config import ImageDetectionModelConfig
from ._types.image_detection_model_alias import ImageDetectionModelAlias
from ._types.image_detection_model_name import ImageDetectionModelName


class ImageDetectionModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_DETECTION_MODEL_",
        extra="ignore",
    )

    aliases: dict[ImageDetectionModelAlias, ImageDetectionModelName] = Field(
        default_factory=lambda: {
            "face": "yunet",
            "object": "dfine",
        }
    )

    presets: dict[ImageDetectionModelName, ImageDetectionModelConfig] = Field(
        default_factory=lambda: {
            "mock": ImageDetectionModelConfig(provider_name="mock"),
            "yunet": ImageDetectionModelConfig(provider_name="yunet"),
            "dfine": ImageDetectionModelConfig(provider_name="dfine"),
        }
    )

    customs: dict[ImageDetectionModelName, ImageDetectionModelConfig] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(ImageDetectionModelSettings)
