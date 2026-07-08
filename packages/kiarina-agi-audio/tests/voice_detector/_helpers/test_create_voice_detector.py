from kiarina.agi.vad_model import vad_model_registry
from kiarina.agi.voice_detector import create_voice_detector


def test_create_voice_detector() -> None:
    vad_model = vad_model_registry.create("mock")
    voice_detector = create_voice_detector(vad_model, threshold=0.7)
    assert voice_detector.settings.threshold == 0.7
    assert voice_detector.vad_model is vad_model
