from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

_MODEL_REVISION = "47534e27c9851bb1128ccc0102f1145e27f23f98"
_MODEL_FILENAME = "face_recognition_sface_2021dec.onnx"


class SFaceImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_SFACE_",
        extra="ignore",
    )

    # OpenCV Zoo SFace (face_recognition_sface_2021dec.onnx).
    model_path: str | Path | None = None

    model_url: str = (
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/"
        f"{_MODEL_REVISION}/models/face_recognition_sface/{_MODEL_FILENAME}"
    )

    model_sha256: str = (
        "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79"
    )

    model_filename: str = _MODEL_FILENAME

    kind: str = "face"

    dimension: int = 128

    # SFace expects an aligned 112x112 face crop.
    input_size: int = 112

    normalize_embedding: bool = True


settings_manager = SettingsManager(SFaceImageEmbeddingProviderSettings)
