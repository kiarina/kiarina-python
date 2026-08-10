from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_segmentation_provider import ImageSegmentationResult
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._instances.image_segmentation_model_registry import (
    image_segmentation_model_registry,
)
from .._models.image_segmentation_model import ImageSegmentationModel
from .._types.image_segmentation_options import ImageSegmentationOptions


async def segment_image(
    pixels: ImagePixels,
    *,
    image_segmentation_options: ImageSegmentationOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> ImageSegmentationResult:
    image_segmentation_options = image_segmentation_options or {}
    image_segmentation_model = image_segmentation_options.get(
        "image_segmentation_model"
    )
    if not isinstance(image_segmentation_model, ImageSegmentationModel):
        image_segmentation_model = image_segmentation_model_registry.resolve(
            image_segmentation_model
        )
    run_context = run_context.with_metadata(
        image_segmentation_model=str(image_segmentation_model)
    )
    return await image_segmentation_model.segment(
        pixels,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
