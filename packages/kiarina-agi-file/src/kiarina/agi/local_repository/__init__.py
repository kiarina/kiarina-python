from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_local_repository import create_local_repository
    from ._schemas.file_path_policy import FilePathPolicy
    from ._services.local_repository import LocalRepository
    from ._settings import LocalRepositorySettings, settings_manager
    from ._types.local_area import LocalArea
    from ._utils.resolve_file_path import resolve_file_path

__all__ = [
    # ._helpers
    "create_local_repository",
    # ._services
    "LocalRepository",
    # ._schemas
    "FilePathPolicy",
    # ._settings
    "LocalRepositorySettings",
    "settings_manager",
    # ._types
    "LocalArea",
    # ._utils
    "resolve_file_path",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_local_repository": "._helpers.create_local_repository",
        # ._services
        "LocalRepository": "._services.local_repository",
        # ._schemas
        "FilePathPolicy": "._schemas.file_path_policy",
        # ._settings
        "LocalRepositorySettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "LocalArea": "._types.local_area",
        # ._utils
        "resolve_file_path": "._utils.resolve_file_path",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
