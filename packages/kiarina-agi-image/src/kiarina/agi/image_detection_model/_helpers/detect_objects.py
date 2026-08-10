from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_provider import DetectedObject
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._instances.image_detection_model_registry import image_detection_model_registry
from .._models.image_detection_model import ImageDetectionModel
from .._types.image_detection_options import ImageDetectionOptions

_DEFAULT_ALIAS = "object"


async def detect_objects(
    pixels: ImagePixels,
    *,
    image_detection_options: ImageDetectionOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> list[DetectedObject]:
    image_detection_options = image_detection_options or {}

    image_detection_model = image_detection_options.get("image_detection_model")

    if not isinstance(image_detection_model, ImageDetectionModel):
        image_detection_model = image_detection_model_registry.resolve(
            image_detection_model or _DEFAULT_ALIAS
        )

    run_context = run_context.with_metadata(
        image_detection_model=str(image_detection_model),
    )

    return await image_detection_model.detect(
        pixels,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
