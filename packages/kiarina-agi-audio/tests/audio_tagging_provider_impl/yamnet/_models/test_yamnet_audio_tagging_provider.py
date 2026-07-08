from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.audio_tagging_provider_impl.yamnet import (
    YamnetAudioTaggingProvider,
    YamnetAudioTaggingProviderSettings,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture
def yamnet_model_path() -> str:
    path = Path("models/yamnet/yamnet.tflite")

    if not path.exists():
        pytest.skip(f"YAMNet TFLite model file not found at {path}")

    return str(path)


@pytest.fixture
def yamnet_class_map_path() -> str:
    path = Path("models/yamnet/yamnet_class_map.csv")

    if not path.exists():
        pytest.skip(f"YAMNet class map file not found at {path}")

    return str(path)


async def test_yamnet_audio_tagging_provider(
    yamnet_model_path: str,
    yamnet_class_map_path: str,
    run_context: RunContext,
) -> None:
    provider = YamnetAudioTaggingProvider(
        YamnetAudioTaggingProviderSettings(
            model_path=yamnet_model_path,
            class_map_path=yamnet_class_map_path,
        )
    )

    # 1 second of silence at 16kHz
    result = await provider.predict(
        np.zeros(16000, dtype=np.float32), 16000, run_context=run_context
    )

    assert len(result) == 521
    assert all(isinstance(p.label, str) and p.label for p in result)
    assert all(0.0 <= p.score <= 1.0 for p in result)


async def test_yamnet_resamples(
    yamnet_model_path: str,
    yamnet_class_map_path: str,
    run_context: RunContext,
) -> None:
    provider = YamnetAudioTaggingProvider(
        YamnetAudioTaggingProviderSettings(
            model_path=yamnet_model_path,
            class_map_path=yamnet_class_map_path,
        )
    )

    # 1 second at 24kHz → should be resampled to 16kHz internally
    result = await provider.predict(
        np.zeros(24000, dtype=np.float32), 24000, run_context=run_context
    )

    assert len(result) == 521
