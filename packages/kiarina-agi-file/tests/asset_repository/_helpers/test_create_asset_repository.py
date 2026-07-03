from typing import Any

from kiarina.agi.file.asset_repository import create_asset_repository


def test_create_asset_repository(run_context: Any) -> None:
    create_asset_repository(run_context)
