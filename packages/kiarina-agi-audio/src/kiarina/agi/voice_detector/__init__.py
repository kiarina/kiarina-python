from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_voice_detector import create_voice_detector
    from ._models.voice_detector import VoiceDetector
    from ._schemas.detect_result import DetectResult
    from ._schemas.voice import Voice
    from ._settings import VoiceDetectorSettings, settings_manager

__all__ = [
    # ._helpers
    "create_voice_detector",
    # ._models
    "VoiceDetector",
    # ._schemas
    "DetectResult",
    "Voice",
    # ._settings
    "VoiceDetectorSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_voice_detector": "._helpers.create_voice_detector",
        # ._models
        "VoiceDetector": "._models.voice_detector",
        # ._schemas
        "DetectResult": "._schemas.detect_result",
        "Voice": "._schemas.voice",
        # ._settings
        "VoiceDetectorSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
