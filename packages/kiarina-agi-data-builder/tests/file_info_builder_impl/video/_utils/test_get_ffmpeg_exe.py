import shutil
import sys

import pytest

from kiarina.agi.file_info_builder_impl.video._utils.get_ffmpeg_exe import (
    get_ffmpeg_exe,
)


def test_get_ffmpeg_exe_without_dependency_or_system_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "imageio_ffmpeg", None)
    monkeypatch.setattr(shutil, "which", lambda name: None)

    with pytest.raises(
        ImportError,
        match=r"kiarina-agi-data-builder\[file-info-builder-video\]",
    ):
        get_ffmpeg_exe()
