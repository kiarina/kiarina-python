import os

from kiarina.agi.file.local_repository import resolve_file_path


def test_resolve_file_path() -> None:
    assert resolve_file_path("~") == os.path.expanduser("~")
