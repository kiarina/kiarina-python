# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

from kiarina.agi.image_detection_provider_impl.mock import (
    create_mock_image_detection_provider,
)


def test_create_mock_image_detection_provider() -> None:
    _ = create_mock_image_detection_provider(
        detections=[{"bbox": [0.1, 0.1, 0.4, 0.4], "score": 0.8, "label": "cat"}]
    )
    assert True
