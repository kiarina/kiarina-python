import numpy as np

from kiarina.agi.image_embedding_model import (
    ImageEmbeddingModel,
    ImageEmbeddingModelConfig,
)
from kiarina.agi.run_context import RunContext


async def test_image_embedding_model(run_context: RunContext) -> None:
    image_embedding_model = ImageEmbeddingModel(
        "example",
        ImageEmbeddingModelConfig(
            provider_name="mock",
            provider_config={
                "embedding": [3.0, 4.0],
                "dimension": 2,
            },
        ),
    )

    print(f"__str__: {image_embedding_model}")
    print(f"provider_name: {image_embedding_model.provider_name}")
    print(f"provider_config: {image_embedding_model.provider_config}")
    print(f"provider: {image_embedding_model.provider}")

    space = image_embedding_model.get_space()
    assert space.kind == "image"
    assert space.dimension == 2

    result = await image_embedding_model.embed(
        np.zeros((32, 24, 3), dtype=np.uint8), run_context=run_context
    )

    assert np.allclose(result.to_numpy(), [0.6, 0.8])
