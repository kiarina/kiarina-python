from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.image_detection_provider_impl.dfine import (
    DFineImageDetectionProvider,
    DFineImageDetectionProviderSettings,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture
def dfine_model_path() -> str:
    path = Path("models/dfine/model.onnx")

    if not path.exists():
        pytest.skip(f"D-FINE ONNX model file not found at {path}")

    return str(path)


@pytest.fixture
def dfine_label_map_path() -> str:
    path = Path("models/dfine/coco_labels.txt")

    if not path.exists():
        pytest.skip(f"D-FINE label map file not found at {path}")

    return str(path)


async def test_dfine_image_detection_provider(
    dfine_model_path: str,
    dfine_label_map_path: str,
    load_rgb_image: Callable[[str], np.ndarray],
    run_context: RunContext,
) -> None:
    provider = DFineImageDetectionProvider(
        DFineImageDetectionProviderSettings(
            model_path=dfine_model_path,
            label_map_path=dfine_label_map_path,
        )
    )

    pixels = load_rgb_image("jpg/apple_1024x1024_138kb.jpg")
    result = await provider.detect(pixels, run_context=run_context)

    assert len(result) >= 1

    for detection in result:
        assert isinstance(detection.label, str) and detection.label
        assert len(detection.bbox) == 4
        assert all(0.0 <= v <= 1.0 for v in detection.bbox)
        assert 0.0 <= detection.score <= 1.0
