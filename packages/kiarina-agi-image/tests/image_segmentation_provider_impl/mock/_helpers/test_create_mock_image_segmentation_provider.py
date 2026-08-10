from kiarina.agi.image_segmentation_provider_impl.mock import (
    create_mock_image_segmentation_provider,
)


def test_create_mock_image_segmentation_provider() -> None:
    provider = create_mock_image_segmentation_provider(
        mask_value=0,
        confidence=0.25,
    )

    assert provider.settings.mask_value == 0
    assert provider.settings.confidence == 0.25
