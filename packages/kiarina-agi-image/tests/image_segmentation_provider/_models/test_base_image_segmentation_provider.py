import threading

import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_segmentation_provider import (
    BaseImageSegmentationProvider,
    ImageSegmentationResult,
)
from kiarina.agi.run_context import RunContext


class ExampleImageSegmentationProvider(BaseImageSegmentationProvider):
    def __init__(self, result: ImageSegmentationResult) -> None:
        super().__init__()
        self.result = result
        self.thread_id: int | None = None
        self.captured_cost_recorder: CostRecorder | None = None

    def _segment(
        self,
        pixels: np.ndarray,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> ImageSegmentationResult:
        self.thread_id = threading.get_ident()
        self.captured_cost_recorder = cost_recorder
        return self.result


def _result(shape: tuple[int, int] = (10, 12)) -> ImageSegmentationResult:
    return ImageSegmentationResult(
        mask=np.zeros(shape, dtype=np.uint8),
        confidence_map=np.zeros(shape, dtype=np.float32),
    )


async def test_base_image_segmentation_provider(run_context: RunContext) -> None:
    provider = ExampleImageSegmentationProvider(_result())
    provider.name = "example"
    caller_thread_id = threading.get_ident()

    result = await provider.segment(
        np.zeros((10, 12, 3), dtype=np.uint8),
        run_context=run_context,
    )

    assert result.mask.shape == (10, 12)
    assert result.confidence_map is not None
    assert provider.thread_id != caller_thread_id
    assert provider.captured_cost_recorder is not None
    assert str(provider) == "ExampleImageSegmentationProvider"


async def test_rejects_non_rgb_shape(run_context: RunContext) -> None:
    with pytest.raises(ValueError, match=r"\[H, W, 3\]"):
        await ExampleImageSegmentationProvider(_result()).segment(
            np.zeros((10, 12), dtype=np.uint8),
            run_context=run_context,
        )


async def test_rejects_non_uint8_input(run_context: RunContext) -> None:
    with pytest.raises(ValueError, match="expects uint8 pixels"):
        await ExampleImageSegmentationProvider(_result()).segment(
            np.zeros((10, 12, 3), dtype=np.float32),
            run_context=run_context,
        )


@pytest.mark.parametrize(
    ("result", "message"),
    [
        (_result((5, 6)), "must match the source image shape"),
        (
            ImageSegmentationResult(mask=np.zeros((10, 12), dtype=np.float32)),
            "mask must have dtype uint8",
        ),
        (
            ImageSegmentationResult(
                mask=np.ones((10, 12), dtype=np.uint8),
            ),
            "mask must contain only 0 or 255",
        ),
        (
            ImageSegmentationResult(
                mask=np.zeros((10, 12), dtype=np.uint8),
                confidence_map=np.zeros((5, 6), dtype=np.float32),
            ),
            "confidence_map must match the source image shape",
        ),
        (
            ImageSegmentationResult(
                mask=np.zeros((10, 12), dtype=np.uint8),
                confidence_map=np.zeros((10, 12), dtype=np.float64),
            ),
            "confidence_map must have dtype float32",
        ),
        (
            ImageSegmentationResult(
                mask=np.zeros((10, 12), dtype=np.uint8),
                confidence_map=np.full((10, 12), np.nan, dtype=np.float32),
            ),
            "confidence_map must contain finite values",
        ),
        (
            ImageSegmentationResult(
                mask=np.zeros((10, 12), dtype=np.uint8),
                confidence_map=np.full((10, 12), 1.1, dtype=np.float32),
            ),
            "confidence_map values must be between",
        ),
    ],
)
async def test_rejects_invalid_result(
    result: ImageSegmentationResult,
    message: str,
    run_context: RunContext,
) -> None:
    with pytest.raises(ValueError, match=message):
        await ExampleImageSegmentationProvider(result).segment(
            np.zeros((10, 12, 3), dtype=np.uint8),
            run_context=run_context,
        )
