from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.speech_to_segments import speech_to_segments
    from ._helpers.speech_to_text import speech_to_text
    from ._instances.asr_model_registry import asr_model_registry
    from ._models.asr_model import ASRModel
    from ._schemas.asr_model_config import ASRModelConfig
    from ._settings import ASRModelSettings, settings_manager
    from ._types.asr_model_alias import ASRModelAlias
    from ._types.asr_model_name import ASRModelName
    from ._types.asr_model_specifier import ASRModelSpecifier
    from ._types.asr_options import ASROptions

__all__ = [
    # ._helpers
    "speech_to_segments",
    "speech_to_text",
    # ._models
    "ASRModel",
    # ._schemas
    "ASRModelConfig",
    # ._instances
    "asr_model_registry",
    # ._settings
    "ASRModelSettings",
    "settings_manager",
    # ._types
    "ASRModelAlias",
    "ASRModelName",
    "ASRModelSpecifier",
    "ASROptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "speech_to_segments": "._helpers.speech_to_segments",
        "speech_to_text": "._helpers.speech_to_text",
        # ._models
        "ASRModel": "._models.asr_model",
        # ._schemas
        "ASRModelConfig": "._schemas.asr_model_config",
        # ._instances
        "asr_model_registry": "._instances.asr_model_registry",
        # ._settings
        "ASRModelSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "ASRModelAlias": "._types.asr_model_alias",
        "ASRModelName": "._types.asr_model_name",
        "ASRModelSpecifier": "._types.asr_model_specifier",
        "ASROptions": "._types.asr_options",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
