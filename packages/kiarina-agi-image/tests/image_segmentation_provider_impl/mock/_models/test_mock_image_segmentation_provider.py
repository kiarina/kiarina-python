import numpy as np

from kiarina.agi.image_segmentation_provider_impl.mock import (
    MockImageSegmentationProvider,
    MockImageSegmentationProviderSettings,
)
from kiarina.agi.run_context import RunContext


async def test_mock_image_segmentation_provider(run_context: RunContext) -> None:
    provider = MockImageSegmentationProvider(
        MockImageSegmentationProviderSettings(mask_value=255, confidence=0.75)
    )

    result = await provider.segment(
        np.zeros((10, 12, 3), dtype=np.uint8),
        run_context=run_context,
    )

    assert np.all(result.mask == 255)
    assert result.confidence_map is not None
    assert np.all(result.confidence_map == np.float32(0.75))
