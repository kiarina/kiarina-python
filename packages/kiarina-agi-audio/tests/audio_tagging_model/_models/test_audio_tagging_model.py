import numpy as np

from kiarina.agi.audio_tagging_model import (
    AudioTaggingModel,
    AudioTaggingModelConfig,
)
from kiarina.agi.run_context import RunContext


async def test_audio_tagging_model(run_context: RunContext) -> None:
    audio_tagging_model = AudioTaggingModel(
        "example",
        AudioTaggingModelConfig(
            provider_name="mock",
            provider_config={
                "predictions": [("Bark", 0.7), ("Meow", 0.2)],
            },
        ),
    )

    print(f"__str__: {audio_tagging_model}")
    print(f"provider_name: {audio_tagging_model.provider_name}")
    print(f"provider_config: {audio_tagging_model.provider_config}")
    print(f"provider: {audio_tagging_model.provider}")

    result = await audio_tagging_model.predict(
        np.zeros(1600), 16000, run_context=run_context
    )

    assert [p.label for p in result] == ["Bark", "Meow"]
    assert [p.score for p in result] == [0.7, 0.2]


async def test_accepts_stereo(run_context: RunContext) -> None:
    audio_tagging_model = AudioTaggingModel(
        "example",
        AudioTaggingModelConfig(
            provider_name="mock",
            provider_config={
                "predictions": [("Bark", 0.7)],
            },
        ),
    )

    result = await audio_tagging_model.predict(
        np.zeros((2, 1600)), 16000, run_context=run_context
    )

    assert [p.label for p in result] == ["Bark"]
