from kiarina.agi.audio_types import AudioSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._instances.asr_model_registry import asr_model_registry
from .._types.asr_options import ASROptions


async def speech_to_text(
    samples: AudioSamples,
    sample_rate: int,
    *,
    asr_options: ASROptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> str:
    asr_options = asr_options or {}

    asr_model = asr_model_registry.resolve(asr_options.get("asr_model"))

    run_context = run_context.with_metadata(
        asr_model=str(asr_model),
    )

    return await asr_model.speech_to_text(
        samples,
        sample_rate,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
