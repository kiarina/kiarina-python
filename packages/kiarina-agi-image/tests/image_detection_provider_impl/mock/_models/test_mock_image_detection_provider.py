import numpy as np

from kiarina.agi.image_detection_provider import DetectedObject
from kiarina.agi.image_detection_provider_impl.mock import (
    MockImageDetectionProvider,
    MockImageDetectionProviderSettings,
)
from kiarina.agi.run_context import RunContext


async def test_mock_image_detection_provider(run_context: RunContext) -> None:
    provider = MockImageDetectionProvider(
        MockImageDetectionProviderSettings(
            detections=[
                DetectedObject(bbox=[0.1, 0.1, 0.4, 0.4], score=0.8, label="cat"),
            ]
        )
    )

    result = await provider.detect(
        np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context
    )

    assert [d.label for d in result] == ["cat"]
    assert result[0].bbox == [0.1, 0.1, 0.4, 0.4]


async def test_mock_image_detection_provider_defaults(run_context: RunContext) -> None:
    provider = MockImageDetectionProvider(MockImageDetectionProviderSettings())

    result = await provider.detect(
        np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context
    )

    assert [d.label for d in result] == ["face", "person"]


async def test_mock_image_detection_provider_returns_copies(
    run_context: RunContext,
) -> None:
    settings = MockImageDetectionProviderSettings()

    result = await provider_detect(settings, run_context)

    # Mutating the returned detection must not affect the settings template.
    result[0].label = "mutated"
    again = await provider_detect(settings, run_context)
    assert again[0].label != "mutated"


async def provider_detect(
    settings: MockImageDetectionProviderSettings,
    run_context: RunContext,
) -> list[DetectedObject]:
    provider = MockImageDetectionProvider(settings)
    return await provider.detect(
        np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context
    )
