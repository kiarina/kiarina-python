from kiarina.agi.video_source_impl.numpy import create_numpy_video_source


def test_create_numpy_video_source() -> None:
    video_source = create_numpy_video_source(fps=2, start_timestamp=100.0)
    assert video_source.settings.fps == 2
    assert video_source.settings.start_timestamp == 100.0
