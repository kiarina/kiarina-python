from kiarina.agi.video_source_impl.queue import create_queue_video_source


def test_create_queue_video_source() -> None:
    _ = create_queue_video_source(x=1)
    assert True
