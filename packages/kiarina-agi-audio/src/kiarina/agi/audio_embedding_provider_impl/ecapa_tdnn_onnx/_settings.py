from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class EcapaTDNNOnnxAudioEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_EMBEDDING_PROVIDER_IMPL_ECAPA_TDNN_ONNX_",
        extra="ignore",
    )

    model_path: str | Path | None = None

    model_url: str = (
        "https://huggingface.co/pranjal-pravesh/ecapa_tdnn_onnx/resolve/"
        "04c3ffe4fd00b3b7853fd57db44e2e531d4817f2/ecapa_tdnn.onnx"
    )

    model_sha256: str = (
        "245eb5995cfffd74494862dee33da2b00c1c2579eb0c6703847784e9901ed458"
    )

    model_filename: str = "ecapa_tdnn.onnx"

    sample_rate: int = 16_000
    dimension: int = 192
    input_name: str | None = None
    output_name: str | None = None
    normalize_embedding: bool = True


settings_manager = SettingsManager(EcapaTDNNOnnxAudioEmbeddingProviderSettings)
