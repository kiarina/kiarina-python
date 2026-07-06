# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import numpy as np

from kiarina.agi.image_detection_model import detect_faces
from kiarina.agi.image_detection_model._helpers import (
    detect_faces as detect_faces_module,
)


async def test_detect_faces_injects_face_alias(run_context, monkeypatch) -> None:
    captured: dict = {}

    async def fake_detect_objects(
        pixels, *, image_detection_options=None, cost_recorder=None, run_context
    ):
        captured["options"] = image_detection_options
        return []

    monkeypatch.setattr(detect_faces_module, "detect_objects", fake_detect_objects)

    await detect_faces(np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context)

    assert captured["options"]["image_detection_model"] == "face"


async def test_detect_faces_preserves_explicit_model(run_context, monkeypatch) -> None:
    captured: dict = {}

    async def fake_detect_objects(
        pixels, *, image_detection_options=None, cost_recorder=None, run_context
    ):
        captured["options"] = image_detection_options
        return []

    monkeypatch.setattr(detect_faces_module, "detect_objects", fake_detect_objects)

    await detect_faces(
        np.zeros((64, 64, 3), dtype=np.uint8),
        image_detection_options={"image_detection_model": "mock"},
        run_context=run_context,
    )

    assert captured["options"]["image_detection_model"] == "mock"
