import pytest

from kiarina.utils.app import AppAlreadyConfiguredError, configure
from kiarina.utils.app._instances.app import app


def test_configure_sets_identity() -> None:
    configure(app_name="kiapi", app_author="kiarina")
    assert app.app_name == "kiapi"
    assert app.app_author == "kiarina"


def test_configure_twice_raises() -> None:
    configure(app_name="kiapi", app_author="kiarina")
    with pytest.raises(AppAlreadyConfiguredError, match="already set"):
        configure(app_name="other", app_author="kiarina")
