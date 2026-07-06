from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class SFaceImageEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_EMBEDDING_PROVIDER_IMPL_SFACE_",
        extra="ignore",
    )

    # OpenCV Zoo SFace (face_recognition_sface_2021dec.onnx).
    model_path: str | Path | None = None

    kind: str = "face"

    dimension: int = 128

    # SFace expects an aligned 112x112 face crop.
    input_size: int = 112

    normalize_embedding: bool = True


settings_manager = SettingsManager(SFaceImageEmbeddingProviderSettings)
