from collections.abc import Callable

import numpy as np
import pytest

from kiarina.agi.image_segmentation_model import segment_image
from kiarina.agi.run_context import RunContext

pytestmark = [pytest.mark.downloads_model]


async def test_segment_image_with_birefnet(
    load_rgb_image: Callable[[str], np.ndarray],
    run_context: RunContext,
) -> None:
    pixels = load_rgb_image("jpg/objects_1536x1024_358kb.jpg")

    result = await segment_image(pixels, run_context=run_context)

    assert result.mask.shape == pixels.shape[:2]
    assert result.mask.dtype == np.uint8
    assert set(np.unique(result.mask)) == {0, 255}
    assert result.confidence_map is not None
    assert result.confidence_map.shape == pixels.shape[:2]
    assert result.confidence_map.dtype == np.float32
    assert np.all((0.0 <= result.confidence_map) & (result.confidence_map <= 1.0))
