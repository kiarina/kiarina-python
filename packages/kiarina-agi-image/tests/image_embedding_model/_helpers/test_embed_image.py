# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import numpy as np

from kiarina.agi.image_embedding_model import embed_image


async def test_embed_image(run_context, cost_recorder) -> None:
    result = await embed_image(
        np.zeros((32, 24, 3), dtype=np.uint8),
        image_embedding_options={
            "image_embedding_model": "mock",
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert np.allclose(result.to_numpy(), [1.0, 0.0, 0.0])
