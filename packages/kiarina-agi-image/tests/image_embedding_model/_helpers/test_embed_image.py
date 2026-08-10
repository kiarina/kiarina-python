import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_embedding_model import embed_image
from kiarina.agi.run_context import RunContext


async def test_embed_image(
    run_context: RunContext, cost_recorder: CostRecorder
) -> None:
    result = await embed_image(
        np.zeros((32, 24, 3), dtype=np.uint8),
        image_embedding_options={
            "image_embedding_model": "mock",
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert np.allclose(result.to_numpy(), [1.0, 0.0, 0.0])
