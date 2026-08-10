import shutil
import sys

import pytest

from kiarina.agi.video_source_impl.file._utils.get_ffmpeg_exe import get_ffmpeg_exe


def test_get_ffmpeg_exe_without_dependency_or_system_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "imageio_ffmpeg", None)
    monkeypatch.setattr(shutil, "which", lambda name: None)

    with pytest.raises(
        ImportError,
        match=r"kiarina-agi-video\[video-source-file\]",
    ):
        get_ffmpeg_exe()
