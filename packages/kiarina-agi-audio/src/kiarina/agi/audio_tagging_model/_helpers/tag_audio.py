from kiarina.agi.audio_tagging_provider import AudioTagPrediction
from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._instances.audio_tagging_model_registry import audio_tagging_model_registry
from .._types.audio_tagging_options import AudioTaggingOptions


async def tag_audio(
    samples: AudioSamples,
    sample_rate: int,
    *,
    audio_tagging_options: AudioTaggingOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> list[AudioTagPrediction]:
    audio_tagging_options = audio_tagging_options or {}

    audio_tagging_model = audio_tagging_model_registry.resolve(
        audio_tagging_options.get("audio_tagging_model")
    )

    run_context = run_context.with_metadata(
        audio_tagging_model=str(audio_tagging_model),
    )

    predictions = await audio_tagging_model.predict(
        samples,
        sample_rate,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    threshold = audio_tagging_options.get("threshold")

    if threshold is not None:
        predictions = [p for p in predictions if p.score >= threshold]

    predictions = sorted(predictions, key=lambda p: p.score, reverse=True)

    top_k = audio_tagging_options.get("top_k")

    if top_k is not None:
        predictions = predictions[:top_k]

    return predictions
