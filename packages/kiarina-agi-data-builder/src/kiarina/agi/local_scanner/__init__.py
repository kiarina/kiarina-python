from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.scan_pattern import scan_pattern
    from ._schemas.local_path_spec import LocalPathSpec
    from ._types.local_path_pattern import LocalPathPattern
    from ._utils.scan_directory import scan_directory

__all__ = [
    # ._types
    "LocalPathPattern",
    # ._helpers
    "scan_pattern",
    # ._schemas
    "LocalPathSpec",
    # ._utils
    "scan_directory",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._types
        "LocalPathPattern": "._types.local_path_pattern",
        # ._helpers
        "scan_pattern": "._helpers.scan_pattern",
        # ._schemas
        "LocalPathSpec": "._schemas.local_path_spec",
        # ._utils
        "scan_directory": "._utils.scan_directory",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
