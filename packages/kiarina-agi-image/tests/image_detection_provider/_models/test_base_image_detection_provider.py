import numpy as np
import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_detection_provider import (
    BaseImageDetectionProvider,
    DetectedObject,
)
from kiarina.agi.run_context import RunContext


class ExampleImageDetectionProvider(BaseImageDetectionProvider):
    def __init__(self, detections: list[DetectedObject]) -> None:
        super().__init__()
        self._detections = detections

    def _detect(
        self,
        pixels: np.ndarray,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[DetectedObject]:
        return self._detections


def _pixels() -> np.ndarray:
    return np.zeros((10, 12, 3), dtype=np.uint8)


async def test_base_image_detection_provider(run_context: RunContext) -> None:
    provider = ExampleImageDetectionProvider(
        [DetectedObject(bbox=[0.1, 0.2, 0.3, 0.4], score=0.7, label="dog")]
    )
    provider.name = "example"

    print(f"__str__: {provider}")
    print(f"name: {provider.name}")

    result = await provider.detect(_pixels(), run_context=run_context)

    assert [d.label for d in result] == ["dog"]
    assert result[0].bbox == [0.1, 0.2, 0.3, 0.4]


async def test_rejects_non_rgb_shape(run_context: RunContext) -> None:
    provider = ExampleImageDetectionProvider([])

    with pytest.raises(ValueError, match=r"\[H, W, 3\]"):
        await provider.detect(
            np.zeros((10, 12), dtype=np.uint8), run_context=run_context
        )


async def test_rejects_non_uint8(run_context: RunContext) -> None:
    provider = ExampleImageDetectionProvider([])

    with pytest.raises(ValueError, match="uint8"):
        await provider.detect(
            np.zeros((10, 12, 3), dtype=np.float32), run_context=run_context
        )


async def test_clips_out_of_range_coordinates(run_context: RunContext) -> None:
    provider = ExampleImageDetectionProvider(
        [
            DetectedObject(
                bbox=[-0.5, 0.2, 1.5, 0.4],
                score=0.9,
                label="face",
                keypoint_type="face_5pt",
                keypoints=[[-0.1, 0.5], [1.2, 0.5]],
            )
        ]
    )
    provider.name = "example"

    result = await provider.detect(_pixels(), run_context=run_context)

    assert result[0].bbox == [0.0, 0.2, 1.0, 0.4]
    assert result[0].keypoints == [[0.0, 0.5], [1.0, 0.5]]


async def test_supplies_null_cost_recorder(run_context: RunContext) -> None:
    captured: dict[str, CostRecorder] = {}

    class CapturingProvider(BaseImageDetectionProvider):
        def _detect(
            self,
            pixels: np.ndarray,
            *,
            cost_recorder: CostRecorder,
            run_context: RunContext,
        ) -> list[DetectedObject]:
            captured["cost_recorder"] = cost_recorder
            return []

    provider = CapturingProvider()
    provider.name = "capturing"

    await provider.detect(_pixels(), run_context=run_context)

    assert captured["cost_recorder"] is not None
