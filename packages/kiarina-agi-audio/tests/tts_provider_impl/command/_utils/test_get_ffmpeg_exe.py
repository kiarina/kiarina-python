import sys

import pytest

from kiarina.agi.tts_provider_impl.command._utils.get_ffmpeg_exe import (
    get_ffmpeg_exe,
)


def test_get_ffmpeg_exe() -> None:
    assert get_ffmpeg_exe()


def test_get_ffmpeg_exe_without_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "imageio_ffmpeg", None)

    with pytest.raises(ImportError, match="tts-provider-command"):
        get_ffmpeg_exe()
