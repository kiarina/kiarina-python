from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_google_tts_provider import create_google_tts_provider
    from ._models.google_tts_provider import GoogleTTSProvider
    from ._settings import GoogleTTSProviderSettings, settings_manager
    from ._types.voice_name import VoiceName

__all__ = [
    # ._helpers
    "create_google_tts_provider",
    # ._models
    "GoogleTTSProvider",
    # ._settings
    "GoogleTTSProviderSettings",
    "settings_manager",
    # ._types
    "VoiceName",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_google_tts_provider": "._helpers.create_google_tts_provider",
        # ._models
        "GoogleTTSProvider": "._models.google_tts_provider",
        # ._settings
        "GoogleTTSProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "VoiceName": "._types.voice_name",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
