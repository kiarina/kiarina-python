from typing import cast

from kiarina.utils.object_registry import ObjectRegistry

from .._services.file_token_store import FileTokenStore
from .._services.token_manager import TokenManager
from .._settings import FirebaseSettings, settings_manager


def _get_default() -> str:
    if settings_manager.active_key is not None:
        return settings_manager.active_key

    return cast(str, settings_manager.user_config.get("default") or "default")


def _get_aliases() -> dict[str, str]:
    return cast(dict[str, str], settings_manager.user_config.get("aliases", {}))


def _get_presets() -> dict[str, FirebaseSettings]:
    return settings_manager.all_settings


def _factory(settings_key: str, settings: FirebaseSettings) -> TokenManager:
    if settings.token_data_file_path is None:
        raise ValueError(
            f"'token_data_file_path' is not configured in the '{settings_key}' settings."
        )

    return TokenManager(
        api_key=settings.api_key.get_secret_value(),
        token_store=FileTokenStore(settings.token_data_file_path),
    )


token_manager_registry = ObjectRegistry[TokenManager, FirebaseSettings](
    expected_type=TokenManager,
    object_label="TokenManager",
    get_default=_get_default,
    get_aliases=_get_aliases,
    get_presets=_get_presets,
    factory=_factory,
)
