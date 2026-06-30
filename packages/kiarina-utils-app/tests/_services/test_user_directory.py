from pathlib import Path

import pytest

from kiarina.utils.app import configure, user_directory
from kiarina.utils.app._settings import settings_manager


@pytest.fixture(autouse=True)
def _clear_settings() -> None:
    settings_manager.user_config = {}
    settings_manager.cli_args = {}


def test_settings_override_takes_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", "/xdg/cache")
    settings_manager.user_config = {"user_cache_dir": "~/custom-cache"}
    configure(app_name="kiapi", app_author="kiarina")

    result = user_directory.get_user_cache_dir()
    assert result == Path.home() / "custom-cache"


def test_xdg_used_when_no_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", "/xdg/cache")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/xdg/config")
    monkeypatch.setenv("XDG_DATA_HOME", "/xdg/data")
    configure(app_name="kiapi", app_author="kiarina")

    assert user_directory.get_user_cache_dir() == Path("/xdg/cache/kiapi")
    assert user_directory.get_user_config_dir() == Path("/xdg/config/kiapi")
    assert user_directory.get_user_data_dir() == Path("/xdg/data/kiapi")


def test_platform_default_when_no_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    configure(app_name="kiapi", app_author="kiarina")

    result = user_directory.get_user_cache_dir()
    assert isinstance(result, Path)
    assert "kiapi" in str(result)
