from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class YamnetAudioTaggingProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_AUDIO_TAGGING_PROVIDER_IMPL_YAMNET_",
        extra="ignore",
    )

    model_path: str | Path | None = None

    model_url: str = (
        "https://tfhub.dev/google/lite-model/yamnet/classification/tflite/1"
        "?lite-format=tflite"
    )

    model_sha256: str = (
        "10c95ea3eb9a7bb4cb8bddf6feb023250381008177ac162ce169694d05c317de"
    )

    model_filename: str = "yamnet.tflite"

    class_map_path: str | Path | None = None

    class_map_url: str = (
        "https://raw.githubusercontent.com/tensorflow/models/"
        "5c597f85268743140854f0e670f2175e8668553a/"
        "research/audioset/yamnet/yamnet_class_map.csv"
    )

    class_map_sha256: str = (
        "cdf24d193e196d9e95912a2667051ae203e92a2ba09449218ccb40ef787c6df2"
    )

    class_map_filename: str = "yamnet_class_map.csv"

    sample_rate: int = 16_000

    aggregation: Literal["mean", "max"] = "mean"

    num_threads: int | None = None


settings_manager = SettingsManager(YamnetAudioTaggingProviderSettings)
