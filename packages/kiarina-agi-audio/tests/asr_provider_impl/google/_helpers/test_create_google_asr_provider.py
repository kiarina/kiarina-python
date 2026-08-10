from kiarina.agi.asr_provider_impl.google import (
    GoogleASRProvider,
    create_google_asr_provider,
)


def test_create_google_asr_provider() -> None:
    provider = create_google_asr_provider(model_name="gemini-3.1-pro-preview")
    assert isinstance(provider, GoogleASRProvider)
    assert provider.settings.model_name == "gemini-3.1-pro-preview"
