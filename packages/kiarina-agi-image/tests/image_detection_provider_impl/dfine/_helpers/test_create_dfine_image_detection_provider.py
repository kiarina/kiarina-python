from kiarina.agi.image_detection_provider_impl.dfine import (
    create_dfine_image_detection_provider,
)


def test_create_dfine_image_detection_provider() -> None:
    _ = create_dfine_image_detection_provider(
        model_path="dummy.onnx",
        label_map_path="dummy.txt",
    )
    assert True
