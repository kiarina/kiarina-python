from .._instances.app import app


def configure(app_name: str, app_author: str) -> None:
    app.app_name = app_name
    app.app_author = app_author
