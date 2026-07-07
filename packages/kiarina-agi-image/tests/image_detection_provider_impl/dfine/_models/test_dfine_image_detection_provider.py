from collections.abc import Callable

import numpy as np

from kiarina.agi.image_detection_provider_impl.dfine import (
    DFineImageDetectionProvider,
    DFineImageDetectionProviderSettings,
)
from kiarina.agi.run_context import RunContext


async def test_dfine_image_detection_provider(
    load_rgb_image: Callable[[str], np.ndarray],
    run_context: RunContext,
) -> None:
    provider = DFineImageDetectionProvider(DFineImageDetectionProviderSettings())

    pixels = load_rgb_image("jpg/apple_1024x1024_138kb.jpg")
    result = await provider.detect(pixels, run_context=run_context)

    assert len(result) >= 1

    for detection in result:
        assert isinstance(detection.label, str) and detection.label
        assert len(detection.bbox) == 4
        assert all(0.0 <= v <= 1.0 for v in detection.bbox)
        assert 0.0 <= detection.score <= 1.0
