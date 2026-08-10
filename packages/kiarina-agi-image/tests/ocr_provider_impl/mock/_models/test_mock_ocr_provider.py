import numpy as np

from kiarina.agi.ocr_provider import OCRResult
from kiarina.agi.ocr_provider_impl.mock import create_mock_ocr_provider
from kiarina.agi.run_context import RunContext


async def test_mock_results_are_copied(run_context: RunContext) -> None:
    configured = OCRResult(
        text="custom",
        score=0.7,
        polygon=[[0.1, 0.1], [0.2, 0.1], [0.2, 0.2], [0.1, 0.2]],
    )
    provider = create_mock_ocr_provider(results=[configured])
    provider.name = "mock"
    results = await provider.ocr(
        np.zeros((10, 12, 3), dtype=np.uint8), run_context=run_context
    )
    results[0].polygon[0][0] = 0.9
    assert configured.polygon[0][0] == 0.1
