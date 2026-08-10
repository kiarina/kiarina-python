from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_openai_tts_provider import create_openai_tts_provider
    from ._models.openai_tts_provider import OpenAITTSProvider
    from ._settings import OpenAITTSProviderSettings, settings_manager

__all__ = [
    # ._helpers
    "create_openai_tts_provider",
    # ._models
    "OpenAITTSProvider",
    # ._settings
    "OpenAITTSProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_openai_tts_provider": "._helpers.create_openai_tts_provider",
        # ._models
        "OpenAITTSProvider": "._models.openai_tts_provider",
        # ._settings
        "OpenAITTSProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
