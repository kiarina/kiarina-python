from kiarina.agi.tts_provider_impl.openai import (
    OpenAITTSProvider,
    create_openai_tts_provider,
)


def test_create_openai_tts_provider() -> None:
    provider = create_openai_tts_provider(model_name="gpt-4o-mini-tts")
    assert isinstance(provider, OpenAITTSProvider)
    assert provider.settings.model_name == "gpt-4o-mini-tts"
