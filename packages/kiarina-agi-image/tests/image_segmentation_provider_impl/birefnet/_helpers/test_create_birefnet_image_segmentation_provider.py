from kiarina.agi.image_segmentation_provider_impl.birefnet import (
    create_birefnet_image_segmentation_provider,
)


def test_create_birefnet_image_segmentation_provider() -> None:
    provider = create_birefnet_image_segmentation_provider(
        model_path="dummy.onnx",
        threshold=0.8,
    )

    assert provider.settings.model_path == "dummy.onnx"
    assert provider.settings.threshold == 0.8
