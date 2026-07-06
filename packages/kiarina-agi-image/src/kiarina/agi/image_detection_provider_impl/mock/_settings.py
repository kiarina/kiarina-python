from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.image_detection_provider import DetectedObject


class MockImageDetectionProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    detections: list[DetectedObject] = Field(
        default_factory=lambda: [
            DetectedObject(bbox=[0.1, 0.1, 0.5, 0.5], score=0.9, label="face"),
            DetectedObject(bbox=[0.4, 0.4, 0.9, 0.9], score=0.8, label="person"),
        ]
    )


settings_manager = SettingsManager(MockImageDetectionProviderSettings)
