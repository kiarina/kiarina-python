from .._exceptions.app_already_configured_error import AppAlreadyConfiguredError
from .._exceptions.app_not_configured_error import AppNotConfiguredError


class App:
    def __init__(self) -> None:
        self._app_name: str | None = None
        self._app_author: str | None = None

    @property
    def app_name(self) -> str:
        if self._app_name is None:
            raise AppNotConfiguredError("App name is not set.")
        return self._app_name

    @app_name.setter
    def app_name(self, value: str) -> None:
        if self._app_name is not None:
            raise AppAlreadyConfiguredError("App name is already set.")
        self._app_name = value

    @property
    def app_author(self) -> str:
        if self._app_author is None:
            raise AppNotConfiguredError("App author is not set.")
        return self._app_author

    @app_author.setter
    def app_author(self, value: str) -> None:
        if self._app_author is not None:
            raise AppAlreadyConfiguredError("App author is already set.")
        self._app_author = value

    def reset(self) -> None:
        self._app_name = None
        self._app_author = None
