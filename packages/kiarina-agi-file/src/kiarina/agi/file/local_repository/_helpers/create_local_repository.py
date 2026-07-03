from kiarina.agi.base.run_context import RunContext

from .._services.local_repository import LocalRepository
from .._settings import settings_manager


def create_local_repository(run_context: RunContext) -> LocalRepository:
    settings = settings_manager.get_settings()
    return LocalRepository(settings, run_context=run_context)
