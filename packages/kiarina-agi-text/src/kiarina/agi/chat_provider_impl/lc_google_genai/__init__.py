from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_lc_google_genai_chat_provider import (
        create_lc_google_genai_chat_provider,
    )
    from ._models.lc_google_genai_chat_provider import LCGoogleGenAIChatProvider
    from ._settings import LCGoogleGenAIChatProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_lc_google_genai_chat_provider",
    # ._models
    "LCGoogleGenAIChatProvider",
    # ._settings
    "LCGoogleGenAIChatProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_lc_google_genai_chat_provider": "._helpers.create_lc_google_genai_chat_provider",
        # ._models
        "LCGoogleGenAIChatProvider": "._models.lc_google_genai_chat_provider",
        # ._settings
        "LCGoogleGenAIChatProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
