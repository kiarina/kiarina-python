from kiarina.agi.run_context import RunContext

from .._instances.asset_repository_registry import asset_repository_registry
from .._settings import settings_manager
from .._types.asset_repository import AssetRepository


def create_asset_repository(run_context: RunContext) -> AssetRepository:
    settings = settings_manager.get_settings()

    return asset_repository_registry.resolve(
        uri_policy=settings.uri_policy,
        run_context=run_context,
    )
