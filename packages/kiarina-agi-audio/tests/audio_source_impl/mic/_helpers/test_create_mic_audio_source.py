import pytest

try:
    from kiarina.agi.audio_source_impl.mic import create_mic_audio_source
except ImportError as exc:
    pytest.skip(str(exc), allow_module_level=True)


def test_create_mic_audio_source() -> None:
    audio_source = create_mic_audio_source(max_queue_size=1)
    assert audio_source.settings.max_queue_size == 1
