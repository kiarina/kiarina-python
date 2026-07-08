from kiarina.agi.scd_model import scd_model_registry
from kiarina.agi.speaker_change_detector import (
    create_speaker_change_detector,
)


def test_create_speaker_change_detector() -> None:
    scd_model = scd_model_registry.create("mock")
    speaker_change_detector = create_speaker_change_detector(
        scd_model,
        threshold=0.7,
    )

    assert speaker_change_detector.settings.threshold == 0.7
    assert speaker_change_detector.scd_model is scd_model
