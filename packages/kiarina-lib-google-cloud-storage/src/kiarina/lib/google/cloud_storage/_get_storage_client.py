from google.cloud import storage
from kiarina.lib.google.auth import get_credentials

from .settings import settings_manager


def get_storage_client(config_key: str | None = None, **kwargs) -> storage.Client:
    settings = settings_manager.get_settings_by_key(config_key)
    credentials = get_credentials(settings.google_auth_config_key)
    return storage.Client(credentials=credentials, **kwargs)
