import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._hello import hello

__version__ = version("kiarina-lib-google-auth")

__all__ = ["hello"]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "hello": "._hello",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
