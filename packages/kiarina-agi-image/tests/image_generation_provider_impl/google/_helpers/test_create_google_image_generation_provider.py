from kiarina.agi.image_generation_provider_impl.google import (
    GoogleImageGenerationProvider,
    create_google_image_generation_provider,
)


def test_create_google_image_generation_provider() -> None:
    provider = create_google_image_generation_provider(
        model_name="gemini-2.5-flash-image",
    )
    assert isinstance(provider, GoogleImageGenerationProvider)
    assert provider.settings.model_name == "gemini-2.5-flash-image"
