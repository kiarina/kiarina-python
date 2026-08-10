import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_segmentation_provider import (
    BaseImageSegmentationProvider,
    ImageSegmentationResult,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._settings import MockImageSegmentationProviderSettings


class MockImageSegmentationProvider(BaseImageSegmentationProvider):
    def __init__(self, settings: MockImageSegmentationProviderSettings) -> None:
        super().__init__()
        self.settings = settings

    def _segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageSegmentationResult:
        shape = pixels.shape[:2]
        mask = np.full(shape, self.settings.mask_value, dtype=np.uint8)
        confidence_map = None
        if self.settings.confidence is not None:
            confidence_map = np.full(shape, self.settings.confidence, dtype=np.float32)
        return ImageSegmentationResult(
            mask=mask,
            confidence_map=confidence_map,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"
