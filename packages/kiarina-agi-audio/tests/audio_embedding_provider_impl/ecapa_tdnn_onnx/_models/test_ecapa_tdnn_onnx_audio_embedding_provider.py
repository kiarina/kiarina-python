from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.audio_embedding_provider_impl.ecapa_tdnn_onnx import (
    EcapaTDNNOnnxAudioEmbeddingProvider,
    EcapaTDNNOnnxAudioEmbeddingProviderSettings,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture
def ecapa_tdnn_onnx_model_path() -> str:
    path = Path("models/ecapa-tdnn-onnx/ecapa_tdnn.onnx")

    if not path.exists():
        pytest.skip(f"ECAPA-TDNN ONNX model file not found at {path}")

    return str(path)


async def test_ecapa_tdnn_onnx_audio_embedding_provider(
    ecapa_tdnn_onnx_model_path: str,
    run_context: RunContext,
) -> None:
    provider = EcapaTDNNOnnxAudioEmbeddingProvider(
        EcapaTDNNOnnxAudioEmbeddingProviderSettings(
            model_path=ecapa_tdnn_onnx_model_path,
        )
    )

    space = provider.get_space()
    assert space.kind == "speaker"
    assert space.space_id.startswith("ecapa-tdnn-onnx:sha256=")
    assert ":dim=192:" in space.space_id
    assert space.dimension == 192

    result = await provider.embed(
        np.zeros(16000, dtype=np.float32), 16000, run_context=run_context
    )

    assert result.kind == "speaker"
    assert result.space_id == space.space_id
    assert result.to_numpy().shape == (192,)
    assert result.to_numpy().dtype == np.float32
    assert np.isclose(np.linalg.norm(result.to_numpy()), 1.0)
