from kiarina.agi.image_generation_provider_impl.mock import (
    MockImageGenerationProvider,
    create_mock_image_generation_provider,
)


def test_create_mock_image_generation_provider() -> None:
    provider = create_mock_image_generation_provider(color=(255, 0, 0), image_width=512)
    assert isinstance(provider, MockImageGenerationProvider)
    assert provider.settings.color == (255, 0, 0)
    assert provider.settings.image_width == 512
