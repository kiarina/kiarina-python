from kiarina.agi.run_context import RunContext

from ...video_generation_provider import VideoGenerationResult, VideoGenerationSessionID
from .._instances.video_generation_model_registry import video_generation_model_registry
from .._models.video_generation_model import VideoGenerationModel
from .._types.video_generation_options import VideoGenerationOptions


async def get_video(
    session_id: VideoGenerationSessionID,
    *,
    video_generation_options: VideoGenerationOptions | None = None,
    run_context: RunContext,
) -> VideoGenerationResult:
    video_generation_options = video_generation_options or {}

    video_generation_model = video_generation_options.get("video_generation_model")

    if not isinstance(video_generation_model, VideoGenerationModel):
        video_generation_model = video_generation_model_registry.resolve(
            video_generation_model
        )

    run_context = run_context.with_metadata(
        video_generation_model=str(video_generation_model),
    )

    return await video_generation_model.get(
        session_id,
        run_context=run_context,
    )
