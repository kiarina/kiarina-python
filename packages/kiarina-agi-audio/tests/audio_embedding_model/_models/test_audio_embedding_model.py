import numpy as np

from kiarina.agi.audio_embedding_model import (
    AudioEmbeddingModel,
    AudioEmbeddingModelConfig,
)
from kiarina.agi.run_context import RunContext


async def test_audio_embedding_model(run_context: RunContext) -> None:
    audio_embedding_model = AudioEmbeddingModel(
        "example",
        AudioEmbeddingModelConfig(
            provider_name="mock",
            provider_config={
                "embedding": [3.0, 4.0],
                "dimension": 2,
            },
        ),
    )

    print(f"__str__: {audio_embedding_model}")
    print(f"provider_name: {audio_embedding_model.provider_name}")
    print(f"provider_config: {audio_embedding_model.provider_config}")
    print(f"provider: {audio_embedding_model.provider}")

    space = audio_embedding_model.get_space()
    assert space.kind == "speaker"
    assert space.dimension == 2

    result = await audio_embedding_model.embed(
        np.zeros(1600), 16000, run_context=run_context
    )

    assert np.allclose(result.to_numpy(), [0.6, 0.8])


async def test_accepts_stereo(run_context: RunContext) -> None:
    audio_embedding_model = AudioEmbeddingModel(
        "example",
        AudioEmbeddingModelConfig(
            provider_name="mock",
            provider_config={
                "embedding": [3.0, 4.0],
                "dimension": 2,
            },
        ),
    )

    result = await audio_embedding_model.embed(
        np.zeros((2, 1600)), 16000, run_context=run_context
    )

    assert np.allclose(result.to_numpy(), [0.6, 0.8])
