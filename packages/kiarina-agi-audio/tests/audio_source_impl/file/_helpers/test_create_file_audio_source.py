from kiarina.agi.audio_source_impl.file import create_file_audio_source


def test_create_file_audio_source() -> None:
    _ = create_file_audio_source(x=1)
    assert True
