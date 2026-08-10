from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_file import create_file
    from ._helpers.create_markdown_file import create_markdown_file
    from ._settings import FileFactorySettings, settings_manager
    from ._types.storage_type import StorageType

__all__ = [
    # ._helpers
    "create_file",
    "create_markdown_file",
    # ._settings
    "FileFactorySettings",
    "settings_manager",
    # ._types
    "StorageType",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_file": "._helpers.create_file",
        "create_markdown_file": "._helpers.create_markdown_file",
        # ._settings
        "FileFactorySettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "StorageType": "._types.storage_type",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
