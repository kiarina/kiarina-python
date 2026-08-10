import numpy as np

from kiarina.agi.audio_embedding_model import embed_audio
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


async def test_embed_audio(
    run_context: RunContext, cost_recorder: CostRecorder
) -> None:
    result = await embed_audio(
        np.zeros(1600),
        16000,
        audio_embedding_options={
            "audio_embedding_model": "mock",
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert np.allclose(result.to_numpy(), [1.0, 0.0, 0.0])
