import os
from collections.abc import Mapping
from typing import Any

from .._settings import GoogleSettings, settings_manager


def get_genai_http_options(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    client_options: Mapping[str, Any],
    timeout: int | None = None,
) -> dict[str, Any]:
    if settings is None:
        settings = settings_manager.get_settings(settings_key)

    http_options: dict[str, Any] = {}

    if timeout is not None:
        http_options["timeout"] = timeout

    if settings.gemini_api_version and not _uses_vertexai(client_options):
        http_options["api_version"] = settings.gemini_api_version

    return http_options


def _uses_vertexai(client_options: Mapping[str, Any]) -> bool:
    vertexai = client_options.get("vertexai")

    if vertexai is not None:
        return bool(vertexai)

    # google-genai resolves an unset `vertexai` from these variables, in this order.
    for name in ("GOOGLE_GENAI_USE_ENTERPRISE", "GOOGLE_GENAI_USE_VERTEXAI"):
        value = os.environ.get(name)

        if value is not None:
            return value.lower() in ("true", "1")

    return False
