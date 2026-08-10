from kiarina.agi.audio_source_impl.numpy import create_numpy_audio_source


def test_create_numpy_audio_source() -> None:
    _ = create_numpy_audio_source(x=1)
    assert True
