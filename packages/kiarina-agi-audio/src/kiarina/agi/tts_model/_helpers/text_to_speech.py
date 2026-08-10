from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from ...tts_provider import AudioFilePath
from .._instances.tts_model_registry import tts_model_registry
from .._models.tts_model import TTSModel
from .._types.tts_options import TTSOptions


async def text_to_speech(
    text: str,
    *,
    tts_options: TTSOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> AudioFilePath:
    tts_options = tts_options or {}

    tts_model = tts_options.get("tts_model")

    if not isinstance(tts_model, TTSModel):
        tts_model = tts_model_registry.resolve(tts_model)

    run_context = run_context.with_metadata(
        tts_model=str(tts_model),
    )

    return await tts_model.text_to_speech(
        text,
        instructions=tts_options.get("instructions"),
        output_format=tts_options.get("output_format") or "wav",
        ignore_cache=tts_options.get("ignore_cache") or False,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
