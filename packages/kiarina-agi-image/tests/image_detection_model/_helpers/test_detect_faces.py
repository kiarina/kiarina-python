import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_model import detect_faces
from kiarina.agi.image_detection_model._helpers import (
    detect_faces as detect_faces_module,
)
from kiarina.agi.image_detection_model._types.image_detection_options import (
    ImageDetectionOptions,
)
from kiarina.agi.image_detection_provider import DetectedObject
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.run_context import RunContext


async def test_detect_faces_injects_face_alias(
    run_context: RunContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, ImageDetectionOptions | None] = {}

    async def fake_detect_objects(
        pixels: ImagePixels,
        *,
        image_detection_options: ImageDetectionOptions | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        captured["options"] = image_detection_options
        return []

    monkeypatch.setattr(detect_faces_module, "detect_objects", fake_detect_objects)

    await detect_faces(np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context)

    options = captured["options"]
    assert options is not None
    assert options["image_detection_model"] == "face"


async def test_detect_faces_preserves_explicit_model(
    run_context: RunContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, ImageDetectionOptions | None] = {}

    async def fake_detect_objects(
        pixels: ImagePixels,
        *,
        image_detection_options: ImageDetectionOptions | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        captured["options"] = image_detection_options
        return []

    monkeypatch.setattr(detect_faces_module, "detect_objects", fake_detect_objects)

    await detect_faces(
        np.zeros((64, 64, 3), dtype=np.uint8),
        image_detection_options={"image_detection_model": "mock"},
        run_context=run_context,
    )

    options = captured["options"]
    assert options is not None
    assert options["image_detection_model"] == "mock"
