from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_provider import DetectedObject
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._types.image_detection_options import ImageDetectionOptions
from .detect_objects import detect_objects

_DEFAULT_ALIAS = "face"


async def detect_faces(
    pixels: ImagePixels,
    *,
    image_detection_options: ImageDetectionOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> list[DetectedObject]:
    image_detection_options = image_detection_options or {}

    if image_detection_options.get("image_detection_model") is None:
        image_detection_options = {
            **image_detection_options,
            "image_detection_model": _DEFAULT_ALIAS,
        }

    return await detect_objects(
        pixels,
        image_detection_options=image_detection_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
