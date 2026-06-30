from kiarina.utils.app import configure, reset
from kiarina.utils.app._instances.app import app


def test_reset_allows_reconfigure() -> None:
    configure(app_name="kiapi", app_author="kiarina")
    reset()
    configure(app_name="other", app_author="someone")
    assert app.app_name == "other"
    assert app.app_author == "someone"
