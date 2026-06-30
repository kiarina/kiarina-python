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
    from ._services import single_instance, user_directory  # noqa: F401

__version__ = version("kiarina-utils-app")

__all__ = [
    # ._exceptions
    "AlreadyRunningError",
    "AppAlreadyConfiguredError",
    "AppNotConfiguredError",
    # ._helpers
    "configure",
    "reset",
    # ._services (exposed as modules)
    "single_instance",
    "user_directory",
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
        # ._services (exposed as modules)
        "single_instance": "._services.single_instance",
        "user_directory": "._services.user_directory",
    }

    try:
        globals()[name] = getattr(import_module(module_map[name], __name__), name)
    except AttributeError:
        globals()[name] = import_module(module_map[name], __name__)

    return globals()[name]
