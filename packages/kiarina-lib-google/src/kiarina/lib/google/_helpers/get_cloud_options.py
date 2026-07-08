from typing import Any

from .._settings import GoogleSettings, settings_manager
from .._types.credentials_cache import CredentialsCache
from .get_credentials import get_credentials


def get_cloud_options(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    scopes: list[str] | None = None,
    cache: CredentialsCache | None = None,
) -> dict[str, Any]:
    if settings is None:
        settings = settings_manager.get_settings(settings_key)

    if settings.type == "default" and not settings.impersonate_service_account:
        return {}

    credentials = get_credentials(
        settings=settings,
        scopes=scopes,
        cache=cache,
    )

    return {"credentials": credentials}
