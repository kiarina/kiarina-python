import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._exceptions.already_running_error import AlreadyRunningError
    from ._exceptions.app_already_configured_error import AppAlreadyConfiguredError
    from ._exceptions.app_not_configured_error import AppNotConfiguredError
    from ._helpers.configure import configure
    from ._helpers.reset import reset
    from ._instances.app import app
    from ._schemas.app import App
    from ._services import single_instance, user_directory
    from ._settings import AppSettings, settings_manager

__version__ = version("kiarina-utils-app")

__all__ = [
    # ._exceptions
    "AlreadyRunningError",
    "AppAlreadyConfiguredError",
    "AppNotConfiguredError",
    # ._helpers
    "configure",
    "reset",
    # ._instances
    "app",
    # ._schemas
    "App",
    # ._services (exposed as modules)
    "single_instance",
    "user_directory",
    # ._settings
    "AppSettings",
    "settings_manager",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        # ._exceptions
        "AlreadyRunningError": "._exceptions.already_running_error",
        "AppAlreadyConfiguredError": "._exceptions.app_already_configured_error",
        "AppNotConfiguredError": "._exceptions.app_not_configured_error",
        # ._helpers
        "configure": "._helpers.configure",
        "reset": "._helpers.reset",
        # ._instances
        "app": "._instances.app",
        # ._schemas
        "App": "._schemas.app",
        # ._services (exposed as modules)
        "single_instance": "._services.single_instance",
        "user_directory": "._services.user_directory",
        # ._settings
        "AppSettings": "._settings",
        "settings_manager": "._settings",
    }

    try:
        globals()[name] = getattr(import_module(module_map[name], __name__), name)
    except AttributeError:
        globals()[name] = import_module(module_map[name], __name__)

    return globals()[name]
