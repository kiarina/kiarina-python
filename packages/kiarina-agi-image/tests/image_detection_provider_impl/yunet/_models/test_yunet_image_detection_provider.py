# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

from pathlib import Path

import pytest

from kiarina.agi.image_detection_provider_impl.yunet import (
    YuNetImageDetectionProvider,
    YuNetImageDetectionProviderSettings,
)


@pytest.fixture
def yunet_model_path() -> str:
    path = Path("models/yunet/face_detection_yunet_2023mar_int8bq.onnx")

    if not path.exists():
        pytest.skip(f"YuNet ONNX model file not found at {path}")

    return str(path)


async def test_yunet_image_detection_provider(
    yunet_model_path,
    load_rgb_image,
    run_context,
) -> None:
    provider = YuNetImageDetectionProvider(
        YuNetImageDetectionProviderSettings(model_path=yunet_model_path)
    )

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
