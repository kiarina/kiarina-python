from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class SileroVADProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VAD_PROVIDER_IMPL_SILERO_",
        extra="ignore",
    )

    model_path: str | Path | None = None

    model_url: str = (
        "https://raw.githubusercontent.com/snakers4/silero-vad/master/"
        "src/silero_vad/data/silero_vad.onnx"
    )

    model_sha256: str = (
        "1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3"
    )

    model_filename: str = "silero_vad.onnx"


settings_manager = SettingsManager(SileroVADProviderSettings)
