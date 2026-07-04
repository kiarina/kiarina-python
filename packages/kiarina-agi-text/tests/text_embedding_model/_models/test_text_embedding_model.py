from typing import Any

import numpy as np

from kiarina.agi.text_embedding_model import (
    TextEmbeddingModel,
    TextEmbeddingModelConfig,
)


async def test_text_embedding_model(run_context: Any) -> None:
    text_embedding_model = TextEmbeddingModel(
        "example",
        TextEmbeddingModelConfig(
            provider_name="mock",
            provider_config={
                "embedding": [3.0, 4.0],
                "dimension": 2,
            },
        ),
    )

    print(f"__str__: {text_embedding_model}")
    print(f"provider_name: {text_embedding_model.provider_name}")
    print(f"provider_config: {text_embedding_model.provider_config}")
    print(f"provider: {text_embedding_model.provider}")

    space = text_embedding_model.get_space()
    assert space.kind == "text"
    assert space.dimension == 2

    result = await text_embedding_model.embed("hello", run_context=run_context)

    assert np.allclose(result.to_numpy(), [0.6, 0.8])
