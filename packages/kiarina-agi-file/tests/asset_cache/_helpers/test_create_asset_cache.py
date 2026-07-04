from kiarina.agi.asset_cache import create_asset_cache
from kiarina.agi.run_context import RunContext


def test_create_asset_cache(run_context: RunContext) -> None:
    create_asset_cache(run_context)
