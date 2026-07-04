from typing import Any

import numpy as np

from kiarina.agi.text_embedding_model import embed_text


async def test_embed_text(run_context: Any, cost_recorder: Any) -> None:
    result = await embed_text(
        "hello",
        text_embedding_options={
            "text_embedding_model": "mock",
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert np.allclose(result.to_numpy(), [1.0, 0.0, 0.0])
