from kiarina.agi.tts_provider_impl.google import (
    create_google_tts_provider,
)


def test_create_google_tts_provider() -> None:
    provider = create_google_tts_provider(model_name="gemini-2.5-pro-preview-tts")
    assert provider.settings.model_name == "gemini-2.5-pro-preview-tts"
