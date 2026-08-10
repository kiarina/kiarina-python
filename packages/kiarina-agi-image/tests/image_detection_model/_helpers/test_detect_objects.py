import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_model import detect_objects
from kiarina.agi.image_detection_model._instances.image_detection_model_registry import (
    image_detection_model_registry,
)
from kiarina.agi.image_detection_model._models.image_detection_model import (
    ImageDetectionModel,
)
from kiarina.agi.image_detection_model._types.image_detection_model_specifier import (
    ImageDetectionModelSpecifier,
)
from kiarina.agi.run_context import RunContext


async def test_detect_objects_with_explicit_mock(
    run_context: RunContext, cost_recorder: CostRecorder
) -> None:
    result = await detect_objects(
        np.zeros((64, 64, 3), dtype=np.uint8),
        image_detection_options={"image_detection_model": "mock"},
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert [d.label for d in result] == ["face", "person"]
    assert all(0.0 <= v <= 1.0 for d in result for v in d.bbox)


async def test_detect_objects_defaults_to_object_alias(
    run_context: RunContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, ImageDetectionModelSpecifier | ImageDetectionModel | None] = {}
    registry = image_detection_model_registry
    real_resolve = registry.resolve

    def fake_resolve(
        object_input: ImageDetectionModelSpecifier | ImageDetectionModel | None = None,
    ) -> ImageDetectionModel:
        captured["input"] = object_input
        return real_resolve("mock")

    monkeypatch.setattr(registry, "resolve", fake_resolve)

    await detect_objects(
        np.zeros((64, 64, 3), dtype=np.uint8),
        run_context=run_context,
    )

    assert captured["input"] == "object"
