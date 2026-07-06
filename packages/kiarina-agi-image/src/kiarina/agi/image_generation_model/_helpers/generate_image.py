from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from ...image_generation_provider import ImageGenerationResult
from .._models.image_generation_model import ImageGenerationModel
from .._services.image_generation_model_registry import image_generation_model_registry
from .._types.image_generation_options import ImageGenerationOptions


async def generate_image(
    prompt: str,
    *,
    file_paths: list[str] | None = None,
    image_generation_options: ImageGenerationOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext | None = None,
) -> ImageGenerationResult:
    run_context = run_context or RunContext()
    image_generation_options = image_generation_options or {}

    image_generation_model = image_generation_options.get("image_generation_model")

    if not isinstance(image_generation_model, ImageGenerationModel):
        image_generation_model = image_generation_model_registry.resolve(
            image_generation_model
        )

    run_context = run_context.with_metadata(
        image_generation_model=str(image_generation_model),
    )

    return await image_generation_model.generate(
        prompt,
        file_paths=file_paths,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
