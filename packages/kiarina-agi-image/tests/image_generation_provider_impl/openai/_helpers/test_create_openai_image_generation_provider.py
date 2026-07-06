# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import pytest

from kiarina.agi.image_generation_provider_impl.openai import (
    OpenAIImageGenerationProvider,
    create_openai_image_generation_provider,
    settings_manager,
)


@pytest.fixture(autouse=True)
def setup():
    settings_manager.cli_args = {
        "model_name": "gpt-image-1",
        "quality": "medium",
        "size": "1024x1024",
    }
    yield
    settings_manager.cli_args = {}


def test_create_openai_image_generation_provider() -> None:
    provider = create_openai_image_generation_provider()
    assert isinstance(provider, OpenAIImageGenerationProvider)
    assert provider.settings.model_name == "gpt-image-1"
    assert provider.settings.quality == "medium"
    assert provider.settings.size == "1024x1024"


def test_create_openai_image_generation_provider_with_config() -> None:
    provider = create_openai_image_generation_provider(
        model_name="gpt-image-1.5",
        quality="high",
        size="1536x1024",
    )
    assert isinstance(provider, OpenAIImageGenerationProvider)
    assert provider.settings.model_name == "gpt-image-1.5"
    assert provider.settings.quality == "high"
    assert provider.settings.size == "1536x1024"
