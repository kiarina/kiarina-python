from kiarina.agi.video_generation_provider_impl.google import (
    GoogleVideoGenerationProvider,
    create_google_video_generation_provider,
)


def test_create_google_video_generation_provider() -> None:
    provider = create_google_video_generation_provider(
        model_name="veo-3.1-fast-generate-preview"
    )
    assert isinstance(provider, GoogleVideoGenerationProvider)
    assert provider.settings.model_name == "veo-3.1-fast-generate-preview"
