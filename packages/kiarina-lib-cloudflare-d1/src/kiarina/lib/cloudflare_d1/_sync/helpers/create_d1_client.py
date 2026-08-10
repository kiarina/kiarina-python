from kiarina.lib.cloudflare import settings_manager as auth_settings_manager

from ..._settings import settings_manager
from ..models.d1_client import D1Client


def create_d1_client(
    settings_key: str | None = None,
    *,
    auth_settings_key: str | None = None,
) -> D1Client:
    settings = settings_manager.get_settings(settings_key)
    auth_settings = auth_settings_manager.get_settings(auth_settings_key)
    return D1Client(settings, auth_settings=auth_settings)
