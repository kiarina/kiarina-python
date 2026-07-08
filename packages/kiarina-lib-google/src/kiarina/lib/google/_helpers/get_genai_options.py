from typing import Any

from .._settings import GoogleSettings, settings_manager
from .._types.credentials_cache import CredentialsCache
from .get_credentials import get_credentials


def get_genai_options(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    scopes: list[str] | None = None,
    cache: CredentialsCache | None = None,
) -> dict[str, Any]:
    if settings is None:
        settings = settings_manager.get_settings(settings_key)

    api_key = settings.api_key.get_secret_value() if settings.api_key else None

    if settings.vertexai is True and api_key is not None:
        return {
            "vertexai": True,
            "api_key": api_key,
        }

    if settings.vertexai is False or (
        settings.vertexai is None and settings.type == "api_key"
    ):
        if api_key is not None:
            return {"api_key": api_key}

        return {}

    if settings.type == "default" and not settings.impersonate_service_account:
        return {}

    options: dict[str, Any] = {
        "vertexai": True,
        "credentials": get_credentials(
            settings=settings,
            scopes=scopes,
            cache=cache,
        ),
    }

    if settings.project_id:
        options["project"] = settings.project_id

    if settings.location:
        options["location"] = settings.location

    return options
