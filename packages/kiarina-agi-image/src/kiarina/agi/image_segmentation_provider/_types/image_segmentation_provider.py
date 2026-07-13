from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._views.image_segmentation_result import ImageSegmentationResult
from .image_segmentation_provider_name import ImageSegmentationProviderName


@runtime_checkable
class ImageSegmentationProvider(Protocol):
    name: ImageSegmentationProviderName

    async def segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageSegmentationResult: ...
