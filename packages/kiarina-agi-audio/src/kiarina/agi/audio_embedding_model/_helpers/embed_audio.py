from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.embedding import Embedding
from kiarina.agi.run_context import RunContext

from .._instances.audio_embedding_model_registry import audio_embedding_model_registry
from .._types.audio_embedding_options import AudioEmbeddingOptions


async def embed_audio(
    samples: AudioSamples,
    sample_rate: int,
    *,
    audio_embedding_options: AudioEmbeddingOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> Embedding:
    audio_embedding_options = audio_embedding_options or {}

    audio_embedding_model = audio_embedding_model_registry.resolve(
        audio_embedding_options.get("audio_embedding_model")
    )

    run_context = run_context.with_metadata(
        audio_embedding_model=str(audio_embedding_model),
    )

    return await audio_embedding_model.embed(
        samples,
        sample_rate,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
