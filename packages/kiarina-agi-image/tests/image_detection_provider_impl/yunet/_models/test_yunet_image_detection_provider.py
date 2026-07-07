from collections.abc import Callable

import numpy as np

from kiarina.agi.image_detection_provider_impl.yunet import (
    YuNetImageDetectionProvider,
    YuNetImageDetectionProviderSettings,
)
from kiarina.agi.run_context import RunContext


async def test_yunet_image_detection_provider(
    load_rgb_image: Callable[[str], np.ndarray],
    run_context: RunContext,
) -> None:
    provider = YuNetImageDetectionProvider(YuNetImageDetectionProviderSettings())

    pixels = load_rgb_image("jpg/apple_1024x1024_138kb.jpg")
    result = await provider.detect(pixels, run_context=run_context)

    assert isinstance(result, list)

    for detection in result:
        assert detection.label == "face"
        assert detection.keypoint_type == "face_5pt"
        assert len(detection.keypoints) == 5
        assert all(0.0 <= v <= 1.0 for v in detection.bbox)
        assert all(0.0 <= c <= 1.0 for point in detection.keypoints for c in point)
        assert 0.0 <= detection.score <= 1.0
