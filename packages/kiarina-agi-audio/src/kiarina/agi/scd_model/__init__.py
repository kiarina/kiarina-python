from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.scd_model_registry import scd_model_registry
    from ._models.scd_model import SCDModel
    from ._schemas.scd_model_config import SCDModelConfig
    from ._settings import SCDModelSettings, settings_manager
    from ._types.scd_model_alias import SCDModelAlias
    from ._types.scd_model_name import SCDModelName
    from ._types.scd_model_specifier import SCDModelSpecifier

__all__ = [
    # ._models
    "SCDModel",
    # ._schemas
    "SCDModelConfig",
    # ._instances
    "scd_model_registry",
    # ._settings
    "SCDModelSettings",
    "settings_manager",
    # ._types
    "SCDModelAlias",
    "SCDModelName",
    "SCDModelSpecifier",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "SCDModel": "._models.scd_model",
        # ._schemas
        "SCDModelConfig": "._schemas.scd_model_config",
        # ._instances
        "scd_model_registry": "._instances.scd_model_registry",
        # ._settings
        "SCDModelSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "SCDModelAlias": "._types.scd_model_alias",
        "SCDModelName": "._types.scd_model_name",
        "SCDModelSpecifier": "._types.scd_model_specifier",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
