from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class ClapOnnxAudioEmbeddingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_EMBEDDING_PROVIDER_IMPL_CLAP_ONNX_",
        extra="ignore",
    )

    model_path: str | Path | None = None

    model_url: str = "https://huggingface.co/Xenova/clap-htsat-unfused/resolve/main/onnx/audio_model.onnx"

    model_sha256: str = (
        "a1c2b43c44f71e0fa841a4b86700886c199bf87699ea45632c4d831bc6c88957"
    )

    model_filename: str = "audio_model.onnx"

    preprocessor_config_path: str | Path | None = None

    preprocessor_config_url: str = (
        "https://huggingface.co/laion/clap-htsat-unfused/resolve/"
        "84bcbbd1d619e407a8216371ddef36e458d95d93/preprocessor_config.json"
    )

    preprocessor_config_sha256: str = (
        "9739f58296aa6f9ac18008fd0150fb2649bc554985fbde86d0a4041c882ac753"
    )

    preprocessor_config_filename: str = "preprocessor_config.json"

    dimension: int = 512
    sample_rate: int = 48_000
    feature_size: int = 64
    fft_window_size: int = 1024
    hop_length: int = 480
    frequency_min: float = 50.0
    frequency_max: float = 14_000.0
    max_length_s: int = 10
    padding: str = "repeatpad"
    truncation: str = "center"
    input_name: str | None = None
    output_name: str | None = None
    normalize_embedding: bool = True
    extra_preprocessor_config: dict[str, int | float | str | bool | None] = Field(
        default_factory=dict
    )


settings_manager = SettingsManager(ClapOnnxAudioEmbeddingProviderSettings)
