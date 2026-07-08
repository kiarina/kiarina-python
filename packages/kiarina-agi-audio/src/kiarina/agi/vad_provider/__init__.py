from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.base_vad_provider import BaseVADProvider
    from ._services.vad_provider_registry import vad_provider_registry
    from ._settings import VADProviderSettings, settings_manager
    from ._types.speech_probability import SpeechProbability
    from ._types.vad_provider import VADProvider
    from ._types.vad_provider_name import VADProviderName

__all__ = [
    # ._models
    "BaseVADProvider",
    # ._services
    "vad_provider_registry",
    # ._settings
    "VADProviderSettings",
    "settings_manager",
    # ._types
    "SpeechProbability",
    "VADProvider",
    "VADProviderName",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "BaseVADProvider": "._models.base_vad_provider",
        # ._services
        "vad_provider_registry": "._services.vad_provider_registry",
        # ._settings
        "VADProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "SpeechProbability": "._types.speech_probability",
        "VADProvider": "._types.vad_provider",
        "VADProviderName": "._types.vad_provider_name",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
