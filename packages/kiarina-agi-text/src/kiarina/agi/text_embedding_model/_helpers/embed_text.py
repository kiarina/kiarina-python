from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding
from kiarina.agi.run_context import RunContext

from .._services.text_embedding_model_registry import text_embedding_model_registry
from .._types.text_embedding_options import TextEmbeddingOptions


async def embed_text(
    text: str,
    *,
    text_embedding_options: TextEmbeddingOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> Embedding:
    text_embedding_options = text_embedding_options or {}

    text_embedding_model = text_embedding_model_registry.resolve(
        text_embedding_options.get("text_embedding_model")
    )

    run_context = run_context.with_metadata(
        text_embedding_model=str(text_embedding_model),
    )

    return await text_embedding_model.embed(
        text,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
