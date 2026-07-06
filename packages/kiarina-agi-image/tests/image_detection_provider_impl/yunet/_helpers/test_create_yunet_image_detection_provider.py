# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

from kiarina.agi.image_detection_provider_impl.yunet import (
    create_yunet_image_detection_provider,
)


def test_create_yunet_image_detection_provider() -> None:
    _ = create_yunet_image_detection_provider(model_path="dummy.onnx")
    assert True
