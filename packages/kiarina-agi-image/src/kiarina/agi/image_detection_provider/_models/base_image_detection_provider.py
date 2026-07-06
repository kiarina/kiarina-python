import asyncio
from abc import ABC, abstractmethod

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._schemas.detected_object import DetectedObject
from .._types.image_detection_provider import ImageDetectionProvider
from .._types.image_detection_provider_name import ImageDetectionProviderName


class BaseImageDetectionProvider(ImageDetectionProvider, ABC):
    def __init__(self) -> None:
        self._name: ImageDetectionProviderName | None = None

    @property
    def name(self) -> ImageDetectionProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("ImageDetectionProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: ImageDetectionProviderName) -> None:
        self._name = value

    async def detect(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        pixels = _validate_pixels(pixels)

        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(image_detection_provider=f"{self}")

        detections = await asyncio.to_thread(
            self._detect,
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        return [_clip_detection(detection) for detection in detections]

    @abstractmethod
    def _detect(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[DetectedObject]: ...

    # Shared pre/post-processing utilities for subclasses.

    @staticmethod
    def _to_bgr(pixels: ImagePixels) -> ImagePixels:
        return np.ascontiguousarray(pixels[..., ::-1])

    @staticmethod
    def _normalize_bbox(
        x1: float, y1: float, x2: float, y2: float, width: int, height: int
    ) -> list[float]:
        return [x1 / width, y1 / height, x2 / width, y2 / height]

    @staticmethod
    def _normalize_point(x: float, y: float, width: int, height: int) -> list[float]:
        return [x / width, y / height]

    def __str__(self) -> str:
        return self.__class__.__name__


def _validate_pixels(pixels: ImagePixels) -> ImagePixels:
    pixels = np.asarray(pixels)

    if pixels.ndim != 3 or pixels.shape[2] != 3:
        raise ValueError(
            "ImageDetectionProvider expects pixels shaped as [H, W, 3] (RGB), "
            f"got shape {pixels.shape}."
        )

    if pixels.dtype != np.uint8:
        raise ValueError(
            f"ImageDetectionProvider expects uint8 pixels, got dtype {pixels.dtype}."
        )

    return pixels


def _clip_detection(detection: DetectedObject) -> DetectedObject:
    detection.bbox = [float(np.clip(value, 0.0, 1.0)) for value in detection.bbox]
    detection.keypoints = [
        [float(np.clip(coord, 0.0, 1.0)) for coord in point]
        for point in detection.keypoints
    ]
    return detection
