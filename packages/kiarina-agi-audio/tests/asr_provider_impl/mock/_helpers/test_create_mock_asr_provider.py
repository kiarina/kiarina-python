from kiarina.agi.asr_provider_impl.mock import (
    MockASRProvider,
    create_mock_asr_provider,
)


def test_create_mock_asr_provider() -> None:
    provider = create_mock_asr_provider(result_text="Custom transcription")
    assert isinstance(provider, MockASRProvider)
    assert provider.settings.result_text == "Custom transcription"
