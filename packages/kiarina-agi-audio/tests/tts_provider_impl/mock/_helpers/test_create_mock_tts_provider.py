from kiarina.agi.tts_provider_impl.mock import (
    MockTTSProvider,
    create_mock_tts_provider,
)


def test_create_mock_tts_provider() -> None:
    provider = create_mock_tts_provider(
        result_audio_file_path="tests/data/audio/sample.wav",
    )
    assert isinstance(provider, MockTTSProvider)
    assert provider.settings.result_audio_file_path == "tests/data/audio/sample.wav"
