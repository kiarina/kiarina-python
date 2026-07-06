from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._instances.image_embedding_model_registry import image_embedding_model_registry
from .._types.image_embedding_options import ImageEmbeddingOptions


async def embed_image(
    pixels: ImagePixels,
    *,
    image_embedding_options: ImageEmbeddingOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> Embedding:
    image_embedding_options = image_embedding_options or {}

    image_embedding_model = image_embedding_model_registry.resolve(
        image_embedding_options.get("image_embedding_model")
    )

    run_context = run_context.with_metadata(
        image_embedding_model=str(image_embedding_model),
    )

    return await image_embedding_model.embed(
        pixels,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
