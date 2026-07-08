from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.vad_model import VADModel
    from ._schemas.vad_model_config import VADModelConfig
    from ._services.vad_model_registry import vad_model_registry
    from ._settings import VADModelSettings, settings_manager
    from ._types.vad_model_alias import VADModelAlias
    from ._types.vad_model_name import VADModelName
    from ._types.vad_model_specifier import VADModelSpecifier

__all__ = [
    # ._models
    "VADModel",
    # ._schemas
    "VADModelConfig",
    # ._services
    "vad_model_registry",
    # ._settings
    "VADModelSettings",
    "settings_manager",
    # ._types
    "VADModelAlias",
    "VADModelName",
    "VADModelSpecifier",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "VADModel": "._models.vad_model",
        # ._schemas
        "VADModelConfig": "._schemas.vad_model_config",
        # ._services
        "vad_model_registry": "._services.vad_model_registry",
        # ._settings
        "VADModelSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "VADModelAlias": "._types.vad_model_alias",
        "VADModelName": "._types.vad_model_name",
        "VADModelSpecifier": "._types.vad_model_specifier",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
