from kiarina.agi.audio_source_impl.queue import create_queue_audio_source


def test_create_queue_audio_source() -> None:
    _ = create_queue_audio_source(max_queue_size=1)
    assert True
