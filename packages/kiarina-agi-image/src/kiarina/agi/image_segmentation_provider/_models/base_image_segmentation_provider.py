import asyncio
from abc import ABC, abstractmethod

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._types.image_segmentation_provider import ImageSegmentationProvider
from .._types.image_segmentation_provider_name import ImageSegmentationProviderName
from .._views.image_segmentation_result import ImageSegmentationResult


class BaseImageSegmentationProvider(ImageSegmentationProvider, ABC):
    def __init__(self) -> None:
        self._name: ImageSegmentationProviderName | None = None

    @property
    def name(self) -> ImageSegmentationProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("ImageSegmentationProvider name is not set.")
        return self._name

    @name.setter
    def name(self, value: ImageSegmentationProviderName) -> None:
        self._name = value

    async def segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageSegmentationResult:
        pixels = _validate_pixels(pixels)
        cost_recorder = cost_recorder or NullCostRecorder()
        run_context = run_context.with_metadata(image_segmentation_provider=str(self))
        result = await asyncio.to_thread(
            self._segment,
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
        return _validate_result(result, pixels.shape[:2])

    @abstractmethod
    def _segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageSegmentationResult: ...

    def __str__(self) -> str:
        return self.__class__.__name__


def _validate_pixels(pixels: ImagePixels) -> ImagePixels:
    pixels = np.asarray(pixels)
    if pixels.ndim != 3 or pixels.shape[2] != 3:
        raise ValueError(
            "ImageSegmentationProvider expects pixels shaped as [H, W, 3] (RGB), "
            f"got shape {pixels.shape}."
        )
    if pixels.dtype != np.uint8:
        raise ValueError(
            f"ImageSegmentationProvider expects uint8 pixels, got dtype {pixels.dtype}."
        )
    return pixels


def _validate_result(
    result: ImageSegmentationResult, image_shape: tuple[int, int]
) -> ImageSegmentationResult:
    mask = np.asarray(result.mask)
    if mask.shape != image_shape:
        raise ValueError(
            "ImageSegmentationResult mask must match the source image shape "
            f"{image_shape}, got {mask.shape}."
        )
    if mask.dtype != np.uint8:
        raise ValueError(
            f"ImageSegmentationResult mask must have dtype uint8, got {mask.dtype}."
        )
    if not np.all((mask == 0) | (mask == 255)):
        raise ValueError("ImageSegmentationResult mask must contain only 0 or 255.")
    result.mask = np.ascontiguousarray(mask)

    if result.confidence_map is not None:
        confidence_map = np.asarray(result.confidence_map)
        if confidence_map.shape != image_shape:
            raise ValueError(
                "ImageSegmentationResult confidence_map must match the source image "
                f"shape {image_shape}, got {confidence_map.shape}."
            )
        if confidence_map.dtype != np.float32:
            raise ValueError(
                "ImageSegmentationResult confidence_map must have dtype float32, "
                f"got {confidence_map.dtype}."
            )
        if not np.all(np.isfinite(confidence_map)):
            raise ValueError(
                "ImageSegmentationResult confidence_map must contain finite values."
            )
        if np.any((confidence_map < 0.0) | (confidence_map > 1.0)):
            raise ValueError(
                "ImageSegmentationResult confidence_map values must be between "
                "0.0 and 1.0."
            )
        result.confidence_map = np.ascontiguousarray(confidence_map)

    return result
