from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.pyannote_output_kind import PyannoteOutputKind


class PyannoteSCDProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_SCD_PROVIDER_IMPL_PYANNOTE_",
        extra="ignore",
    )

    model_path: str | Path | None = None

    model_url: str = (
        "https://huggingface.co/onnx-community/pyannote-segmentation-3.0/"
        "resolve/main/onnx/model.onnx"
    )

    model_sha256: str = (
        "057ee564753071c0b09b5b611648b50ac188d50846bff5f01e9f7bbf1591ea25"
    )

    model_filename: str = "model.onnx"

    sample_rate: int = 16_000

    window_duration: float = 10.0

    num_speakers: int = 3

    max_speakers_per_frame: int = 2

    output_kind: PyannoteOutputKind = "auto"

    input_name: str | None = None

    output_name: str | None = None


settings_manager = SettingsManager(PyannoteSCDProviderSettings)
