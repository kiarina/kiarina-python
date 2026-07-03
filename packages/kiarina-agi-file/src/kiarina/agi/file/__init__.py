from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.get_file_blob import get_file_blob
    from ._types.file_path import FilePath
    from ._types.uri_or_file_path import URIOrFilePath

__all__ = [
    # ._helpers
    "get_file_blob",
    # ._types
    "FilePath",
    "URIOrFilePath",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "get_file_blob": "._helpers.get_file_blob",
        # ._types
        "FilePath": "._types.file_path",
        "URIOrFilePath": "._types.uri_or_file_path",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
