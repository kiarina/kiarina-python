# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import numpy as np

from kiarina.agi.image_detection_model import detect_objects
from kiarina.agi.image_detection_model._helpers import (
    detect_objects as detect_objects_module,
)


async def test_detect_objects_with_explicit_mock(run_context, cost_recorder) -> None:
    result = await detect_objects(
        np.zeros((64, 64, 3), dtype=np.uint8),
        image_detection_options={"image_detection_model": "mock"},
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert [d.label for d in result] == ["face", "person"]
    assert all(0.0 <= v <= 1.0 for d in result for v in d.bbox)


async def test_detect_objects_defaults_to_object_alias(
    run_context, monkeypatch
) -> None:
    captured: dict = {}
    registry = detect_objects_module.image_detection_model_registry
    real_resolve = registry.resolve

    def fake_resolve(object_input=None, **kwargs):
        captured["input"] = object_input
        return real_resolve("mock")

    monkeypatch.setattr(registry, "resolve", fake_resolve)

    await detect_objects(
        np.zeros((64, 64, 3), dtype=np.uint8),
        run_context=run_context,
    )

    assert captured["input"] == "object"
