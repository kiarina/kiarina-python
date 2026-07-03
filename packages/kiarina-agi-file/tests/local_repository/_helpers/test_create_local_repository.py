from typing import Any

from kiarina.agi.file.local_repository import create_local_repository


def test_create_local_repository(run_context: Any) -> None:
    create_local_repository(run_context)
