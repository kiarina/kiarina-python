from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_speaker_change_detector import (
        create_speaker_change_detector,
    )
    from ._models.speaker_change_detector import SpeakerChangeDetector
    from ._schemas.speech import Speech
    from ._settings import SpeakerChangeDetectorSettings, settings_manager
    from ._types.speaker_kind import SpeakerKind

__all__ = [
    "create_speaker_change_detector",
    "SpeakerChangeDetector",
    "Speech",
    "SpeakerChangeDetectorSettings",
    "settings_manager",
    "SpeakerKind",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_speaker_change_detector": "._helpers.create_speaker_change_detector",
        "SpeakerChangeDetector": "._models.speaker_change_detector",
        "Speech": "._schemas.speech",
        "SpeakerChangeDetectorSettings": "._settings",
        "settings_manager": "._settings",
        "SpeakerKind": "._types.speaker_kind",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
