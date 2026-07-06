# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

from kiarina.agi.image_generation_provider_impl.mock import (
    MockImageGenerationProvider,
    create_mock_image_generation_provider,
)


def test_create_mock_image_generation_provider():
    provider = create_mock_image_generation_provider(color=(255, 0, 0), image_width=512)
    assert isinstance(provider, MockImageGenerationProvider)
    assert provider.settings.color == (255, 0, 0)
    assert provider.settings.image_width == 512
