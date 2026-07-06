from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class YuNetImageDetectionProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_YUNET_",
        extra="ignore",
    )

    # NOTE: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
    model_path: str | Path | None = None

    label: str = "face"

    score_threshold: float = 0.9

    nms_threshold: float = 0.3

    top_k: int = 5000


settings_manager = SettingsManager(YuNetImageDetectionProviderSettings)
