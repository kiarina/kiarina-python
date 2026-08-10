import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.detect_extension import detect_extension
    from ._helpers.extract_extension import extract_extension
    from ._settings import settings_manager

__version__ = "1.0.0"

__all__ = [
    "detect_extension",
    "extract_extension",
    "settings_manager",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "detect_extension": "._helpers.detect_extension",
        "extract_extension": "._helpers.extract_extension",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
