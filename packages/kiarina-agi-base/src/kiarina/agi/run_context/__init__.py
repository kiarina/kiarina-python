from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.get_node_id import get_node_id
    from ._models.run_context import RunContext
    from ._settings import RunContextSettings, settings_manager
    from ._types.id_str import IDStr
    from ._types.time_zone import TimeZone

__all__ = [
    # ._helpers
    "get_node_id",
    # ._models
    "RunContext",
    # ._settings
    "RunContextSettings",
    "settings_manager",
    # ._types
    "IDStr",
    "TimeZone",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        # ._helpers
        "get_node_id": "._helpers.get_node_id",
        # ._models
        "RunContext": "._models.run_context",
        # ._settings
        "RunContextSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "IDStr": "._types.id_str",
        "TimeZone": "._types.time_zone",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
