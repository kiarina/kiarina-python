import pytest


def test_create_camera_video_source() -> None:
    cv2 = pytest.importorskip("cv2")
    assert cv2 is not None

    from kiarina.agi.video_source_impl.camera import create_camera_video_source

    video_source = create_camera_video_source(width=640, height=480)
    assert video_source.settings.width == 640
    assert video_source.settings.height == 480
