from typing import Any

from kiarina.agi.scd_model import SCDModel

from .._models.speaker_change_detector import SpeakerChangeDetector
from .._settings import SpeakerChangeDetectorSettings, settings_manager


def create_speaker_change_detector(
    scd_model: SCDModel, **kwargs: Any
) -> SpeakerChangeDetector:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = SpeakerChangeDetectorSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return SpeakerChangeDetector(scd_model, settings)
