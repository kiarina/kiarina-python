from io import StringIO

import pytest

from kiarina.agi.base.console_utils import stderr_color


class _FakeStderr(StringIO):
    def __init__(self, *, is_tty: bool) -> None:
        super().__init__()
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


def test_stderr_color_resets_color_when_body_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = _FakeStderr(is_tty=True)
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(RuntimeError, match="boom"):
        with stderr_color("black"):
            print("during", file=stderr)
            raise RuntimeError("boom")

    assert stderr.getvalue() == "\033[90mduring\n\033[0m"


def test_stderr_color_skips_color_codes_when_stderr_is_not_tty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = _FakeStderr(is_tty=False)
    monkeypatch.setattr("sys.stderr", stderr)

    with stderr_color("black"):
        print("during", file=stderr)

    assert stderr.getvalue() == "during\n"
