import cv2
import numpy as np
import pytest

from kiarina.agi.ocr_provider_impl.rapidocr import (
    RapidOCRProvider,
    RapidOCRProviderSettings,
)
from kiarina.agi.run_context import RunContext

pytestmark = [pytest.mark.downloads_model]


async def test_rapidocr_provider(
    run_context: RunContext,
) -> None:
    provider = RapidOCRProvider(
        RapidOCRProviderSettings(text_score=0.6, box_threshold=0.7)
    )
    provider.name = "rapidocr"

    pixels = np.full((160, 640, 3), 255, dtype=np.uint8)
    cv2.putText(
        pixels,
        "HELLO 123",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        2.5,
        (0, 0, 0),
        5,
        cv2.LINE_AA,
    )
    results = await provider.ocr(pixels, run_context=run_context)

    texts = [result.text for result in results]
    assert any("HELLO" in text for text in texts)
    assert any("123" in text for text in texts)
    assert all(
        0.0 <= coordinate <= 1.0
        for result in results
        for point in result.polygon
        for coordinate in point
    )


async def test_empty_output(run_context: RunContext) -> None:
    provider = RapidOCRProvider(RapidOCRProviderSettings())
    provider.name = "rapidocr"

    results = await provider.ocr(
        np.full((64, 64, 3), 255, dtype=np.uint8),
        run_context=run_context,
    )

    assert results == []
