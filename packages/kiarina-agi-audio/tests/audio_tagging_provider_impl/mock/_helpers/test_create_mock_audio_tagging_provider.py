from kiarina.agi.audio_tagging_provider_impl.mock import (
    create_mock_audio_tagging_provider,
)


def test_create_mock_audio_tagging_provider() -> None:
    _ = create_mock_audio_tagging_provider(predictions=[("Bark", 0.7)])
    assert True
