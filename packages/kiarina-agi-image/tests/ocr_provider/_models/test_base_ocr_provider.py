import threading

import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.ocr_provider import BaseOCRProvider, OCRResult
from kiarina.agi.run_context import RunContext


class ExampleOCRProvider(BaseOCRProvider):
    def __init__(self, results: list[OCRResult]) -> None:
        super().__init__()
        self.results = results
        self.thread_id: int | None = None
        self.captured_cost_recorder: CostRecorder | None = None

    def _ocr(
        self,
        pixels: np.ndarray,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[OCRResult]:
        self.thread_id = threading.get_ident()
        self.captured_cost_recorder = cost_recorder
        return self.results


def _pixels() -> np.ndarray:
    return np.zeros((10, 12, 3), dtype=np.uint8)


async def test_base_ocr_provider(run_context: RunContext) -> None:
    provider = ExampleOCRProvider(
        [
            OCRResult(
                text="text",
                score=0.8,
                polygon=[[-0.1, 0.2], [1.1, 0.2], [1.1, 0.4], [-0.1, 0.4]],
            )
        ]
    )
    provider.name = "example"
    caller_thread_id = threading.get_ident()

    results = await provider.ocr(_pixels(), run_context=run_context)

    assert results[0].polygon == [[0.0, 0.2], [1.0, 0.2], [1.0, 0.4], [0.0, 0.4]]
    assert provider.thread_id != caller_thread_id
    assert provider.captured_cost_recorder is not None
    assert str(provider) == "ExampleOCRProvider"


async def test_rejects_non_rgb_shape(run_context: RunContext) -> None:
    with pytest.raises(ValueError, match=r"\[H, W, 3\]"):
        await ExampleOCRProvider([]).ocr(
            np.zeros((10, 12), dtype=np.uint8), run_context=run_context
        )


async def test_rejects_non_uint8(run_context: RunContext) -> None:
    with pytest.raises(ValueError, match="uint8"):
        await ExampleOCRProvider([]).ocr(
            np.zeros((10, 12, 3), dtype=np.float32), run_context=run_context
        )


async def test_returns_empty_results(run_context: RunContext) -> None:
    assert await ExampleOCRProvider([]).ocr(_pixels(), run_context=run_context) == []
