from typing import Any

from kiarina.agi.vad_model import VADModel

from .._models.voice_detector import VoiceDetector
from .._settings import VoiceDetectorSettings, settings_manager


def create_voice_detector(vad_model: VADModel, **kwargs: Any) -> VoiceDetector:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = VoiceDetectorSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return VoiceDetector(vad_model, settings)
