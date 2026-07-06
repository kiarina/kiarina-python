from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._schemas.detected_object import DetectedObject
from .image_detection_provider_name import ImageDetectionProviderName


@runtime_checkable
class ImageDetectionProvider(Protocol):
    name: ImageDetectionProviderName

    async def detect(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[DetectedObject]: ...
