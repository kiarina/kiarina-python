from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_google_asr_provider import create_google_asr_provider
    from ._models.google_asr_provider import GoogleASRProvider
    from ._settings import GoogleASRProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_google_asr_provider",
    # ._models
    "GoogleASRProvider",
    # ._settings
    "GoogleASRProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_google_asr_provider": "._helpers.create_google_asr_provider",
        # ._models
        "GoogleASRProvider": "._models.google_asr_provider",
        # ._settings
        "GoogleASRProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
