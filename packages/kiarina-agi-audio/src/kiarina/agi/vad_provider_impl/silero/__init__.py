from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_silero_vad_provider import create_silero_vad_provider
    from ._models.silero_vad_provider import SileroVADProvider
    from ._settings import SileroVADProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_silero_vad_provider",
    # ._models
    "SileroVADProvider",
    # ._settings
    "SileroVADProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_silero_vad_provider": "._helpers.create_silero_vad_provider",
        # ._models
        "SileroVADProvider": "._models.silero_vad_provider",
        # ._settings
        "SileroVADProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
