import pytest


def test_create_file_video_source() -> None:
    pytest.importorskip("imageio_ffmpeg")
    from kiarina.agi.video_source_impl.file import create_file_video_source

    video_source = create_file_video_source(fps=2, start_timestamp=100.0)
    assert video_source.settings.fps == 2
    assert video_source.settings.start_timestamp == 100.0
