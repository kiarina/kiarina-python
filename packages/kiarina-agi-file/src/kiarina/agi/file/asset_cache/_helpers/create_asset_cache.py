from kiarina.agi.base.run_context import RunContext

from .._services.asset_cache import AssetCache
from .._settings import settings_manager


def create_asset_cache(run_context: RunContext) -> AssetCache:
    return AssetCache(settings_manager.get_settings(), run_context=run_context)
