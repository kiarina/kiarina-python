from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.audio_embedding_provider_impl.clap_onnx import (
    ClapOnnxAudioEmbeddingProvider,
    ClapOnnxAudioEmbeddingProviderSettings,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture
def clap_onnx_model_path() -> str:
    path = Path("models/clap-htsat-unfused-onnx/model.onnx")

    if not path.exists():
        pytest.skip(f"CLAP ONNX model file not found at {path}")

    return str(path)


@pytest.fixture
def clap_preprocessor_config_path() -> str:
    path = Path("models/clap-htsat-unfused/preprocessor_config.json")

    if not path.exists():
        pytest.skip(f"CLAP preprocessor config file not found at {path}")

    return str(path)


async def test_clap_onnx_audio_embedding_provider(
    clap_onnx_model_path: str,
    clap_preprocessor_config_path: str,
    run_context: RunContext,
) -> None:
    provider = ClapOnnxAudioEmbeddingProvider(
        ClapOnnxAudioEmbeddingProviderSettings(
            model_path=clap_onnx_model_path,
            preprocessor_config_path=clap_preprocessor_config_path,
        )
    )

    space = provider.get_space()
    assert space.kind == "sound"
    assert space.space_id.startswith("clap-onnx:sha256=")
    assert ":dim=512:" in space.space_id
    assert space.dimension == 512

    samples = np.sin(np.linspace(0.0, 2.0 * np.pi * 440, 48000)).astype(np.float32)
    result = await provider.embed(samples, 48000, run_context=run_context)

    assert result.kind == "sound"
    assert result.space_id == space.space_id
    assert ":pre=logmel-v1:" in result.space_id
    assert result.to_numpy().shape == (512,)
    assert result.to_numpy().dtype == np.float32
    assert np.isclose(np.linalg.norm(result.to_numpy()), 1.0)
    assert result.metadata["preprocessor"] == "clap-log-mel-numpy"


def test_clap_onnx_input_features(
    clap_onnx_model_path: str,
    clap_preprocessor_config_path: str,
) -> None:
    provider = ClapOnnxAudioEmbeddingProvider(
        ClapOnnxAudioEmbeddingProviderSettings(
            model_path=clap_onnx_model_path,
            preprocessor_config_path=clap_preprocessor_config_path,
        )
    )

    input_features, is_longer = provider._extract_input_features(
        np.zeros(48000, dtype=np.float32)
    )

    assert input_features.shape == (1, 1, 1001, 64)
    assert input_features.dtype == np.float32
    assert is_longer.tolist() == [[False]]
