import os
from pathlib import Path

from platformdirs import PlatformDirs

from .._instances.app import app
from .._settings import settings_manager


def get_user_cache_dir() -> Path:
    settings = settings_manager.settings
    return _resolve(settings.user_cache_dir, "XDG_CACHE_HOME", "cache")


def get_user_config_dir() -> Path:
    settings = settings_manager.settings
    return _resolve(settings.user_config_dir, "XDG_CONFIG_HOME", "config")


def get_user_data_dir() -> Path:
    settings = settings_manager.settings
    return _resolve(settings.user_data_dir, "XDG_DATA_HOME", "data")


def _resolve(override: str | None, xdg_env: str, kind: str) -> Path:
    if override:
        return Path(os.path.expanduser(override))

    if xdg_home := os.getenv(xdg_env):
        return Path(xdg_home) / app.app_name

    platform_dirs = PlatformDirs(
        appname=app.app_name,
        appauthor=app.app_author,
    )

    return Path(getattr(platform_dirs, f"user_{kind}_dir"))
