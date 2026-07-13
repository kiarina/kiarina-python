from collections.abc import Callable

import numpy as np
import pytest

from kiarina.agi.image_segmentation_provider_impl.birefnet import (
    BiRefNetImageSegmentationProvider,
    BiRefNetImageSegmentationProviderSettings,
)
from kiarina.agi.run_context import RunContext

pytestmark = [pytest.mark.downloads_model]


@pytest.mark.downloads_model
async def test_birefnet_image_segmentation_provider(
    load_rgb_image: Callable[[str], np.ndarray],
    run_context: RunContext,
) -> None:
    provider = BiRefNetImageSegmentationProvider(
        BiRefNetImageSegmentationProviderSettings()
    )
    provider.name = "birefnet"
    pixels = load_rgb_image("jpg/miineko2_1086x1448_219kb.jpg")

    result = await provider.segment(pixels, run_context=run_context)

    assert result.mask.shape == pixels.shape[:2]
    assert result.mask.dtype == np.uint8
    assert set(np.unique(result.mask)) == {0, 255}
    assert result.confidence_map is not None
    assert result.confidence_map.shape == pixels.shape[:2]
    assert result.confidence_map.dtype == np.float32
    assert np.any((result.confidence_map > 0.0) & (result.confidence_map < 1.0))
    assert provider.session.get_providers()[0] == "CPUExecutionProvider"
