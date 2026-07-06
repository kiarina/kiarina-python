from dataclasses import replace

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_provider import (
    BaseImageDetectionProvider,
    DetectedObject,
)
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._settings import MockImageDetectionProviderSettings


class MockImageDetectionProvider(BaseImageDetectionProvider):
    def __init__(self, settings: MockImageDetectionProviderSettings) -> None:
        super().__init__()
        self.settings: MockImageDetectionProviderSettings = settings

    def _detect(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        return [replace(detection) for detection in self.settings.detections]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(mock)"
