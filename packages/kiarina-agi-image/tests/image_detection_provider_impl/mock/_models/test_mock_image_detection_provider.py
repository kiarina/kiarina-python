# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import numpy as np

from kiarina.agi.image_detection_provider import DetectedObject
from kiarina.agi.image_detection_provider_impl.mock import (
    MockImageDetectionProvider,
    MockImageDetectionProviderSettings,
)


async def test_mock_image_detection_provider(run_context) -> None:
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


async def test_mock_image_detection_provider_defaults(run_context) -> None:
    provider = MockImageDetectionProvider(MockImageDetectionProviderSettings())

    result = await provider.detect(
        np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context
    )

    assert [d.label for d in result] == ["face", "person"]


async def test_mock_image_detection_provider_returns_copies(run_context) -> None:
    settings = MockImageDetectionProviderSettings()

    result = await provider_detect(settings, run_context)

    # Mutating the returned detection must not affect the settings template.
    result[0].label = "mutated"
    again = await provider_detect(settings, run_context)
    assert again[0].label != "mutated"


async def provider_detect(settings, run_context):
    provider = MockImageDetectionProvider(settings)
    return await provider.detect(
        np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context
    )
