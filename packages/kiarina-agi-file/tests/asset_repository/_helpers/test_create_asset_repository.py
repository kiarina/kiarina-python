from kiarina.agi.asset_repository import create_asset_repository
from kiarina.agi.run_context import RunContext


def test_create_asset_repository(run_context: RunContext) -> None:
    create_asset_repository(run_context)
