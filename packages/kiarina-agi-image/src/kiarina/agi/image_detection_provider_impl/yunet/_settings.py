from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

_MODEL_REVISION = "47534e27c9851bb1128ccc0102f1145e27f23f98"
_MODEL_FILENAME = "face_detection_yunet_2023mar_int8bq.onnx"


class YuNetImageDetectionProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_YUNET_",
        extra="ignore",
    )

    # NOTE: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
    model_path: str | Path | None = None

    model_url: str = (
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/"
        f"{_MODEL_REVISION}/models/face_detection_yunet/{_MODEL_FILENAME}"
    )

    model_sha256: str = (
        "49f000ec501fef24739071fc7e68267d32209045b6822c0c72dce1da25726f10"
    )

    model_filename: str = _MODEL_FILENAME

    label: str = "face"

    score_threshold: float = 0.9

    nms_threshold: float = 0.3

    top_k: int = 5000


settings_manager = SettingsManager(YuNetImageDetectionProviderSettings)
