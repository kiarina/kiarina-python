from kiarina.agi.chat_provider_impl.lc_google_genai._helpers.create_lc_google_genai_chat_provider import (
    create_lc_google_genai_chat_provider,
)


def test_create_lc_google_genai_chat_provider() -> None:
    provider = create_lc_google_genai_chat_provider(temperature=0.7)
    assert provider.settings.temperature == 0.7
