import pytest

from kiarina.utils.app import AppAlreadyConfiguredError, AppNotConfiguredError
from kiarina.utils.app._schemas.app import App


def test_set_and_get() -> None:
    app = App()
    app.app_name = "kiapi"
    app.app_author = "kiarina"
    assert app.app_name == "kiapi"
    assert app.app_author == "kiarina"


def test_get_before_set_raises() -> None:
    app = App()
    with pytest.raises(AppNotConfiguredError, match="not set"):
        _ = app.app_name
    with pytest.raises(AppNotConfiguredError, match="not set"):
        _ = app.app_author


def test_set_twice_raises() -> None:
    app = App()
    app.app_name = "kiapi"
    app.app_author = "kiarina"
    with pytest.raises(AppAlreadyConfiguredError, match="already set"):
        app.app_name = "other"
    with pytest.raises(AppAlreadyConfiguredError, match="already set"):
        app.app_author = "someone"


def test_reset_clears_identity() -> None:
    app = App()
    app.app_name = "kiapi"
    app.app_author = "kiarina"
    app.reset()
    app.app_name = "other"
    app.app_author = "someone"
    assert app.app_name == "other"
    assert app.app_author == "someone"
