import asyncio
from abc import ABC, abstractmethod

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext

from .._types.ocr_provider import OCRProvider
from .._types.ocr_provider_name import OCRProviderName
from .._views.ocr_result import OCRResult


class BaseOCRProvider(OCRProvider, ABC):
    def __init__(self) -> None:
        self._name: OCRProviderName | None = None

    @property
    def name(self) -> OCRProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("OCRProvider name is not set.")
        return self._name

    @name.setter
    def name(self, value: OCRProviderName) -> None:
        self._name = value

    async def ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[OCRResult]:
        pixels = _validate_pixels(pixels)
        cost_recorder = cost_recorder or NullCostRecorder()
        run_context = run_context.with_metadata(ocr_provider=str(self))
        results = await asyncio.to_thread(
            self._ocr,
            pixels,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
        return [_clip_result(result) for result in results]

    @abstractmethod
    def _ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[OCRResult]: ...

    @staticmethod
    def _to_bgr(pixels: ImagePixels) -> ImagePixels:
        return np.ascontiguousarray(pixels[..., ::-1])

    def __str__(self) -> str:
        return self.__class__.__name__


def _validate_pixels(pixels: ImagePixels) -> ImagePixels:
    pixels = np.asarray(pixels)
    if pixels.ndim != 3 or pixels.shape[2] != 3:
        raise ValueError(
            "OCRProvider expects pixels shaped as [H, W, 3] (RGB), "
            f"got shape {pixels.shape}."
        )
    if pixels.dtype != np.uint8:
        raise ValueError(f"OCRProvider expects uint8 pixels, got dtype {pixels.dtype}.")
    return pixels


def _clip_result(result: OCRResult) -> OCRResult:
    result.polygon = [
        [float(np.clip(value, 0.0, 1.0)) for value in point] for point in result.polygon
    ]
    return result
