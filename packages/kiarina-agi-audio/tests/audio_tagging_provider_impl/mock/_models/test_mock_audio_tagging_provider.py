import numpy as np

from kiarina.agi.audio_tagging_provider_impl.mock import (
    MockAudioTaggingProvider,
    MockAudioTaggingProviderSettings,
)
from kiarina.agi.run_context import RunContext


async def test_mock_audio_tagging_provider(run_context: RunContext) -> None:
    provider = MockAudioTaggingProvider(
        MockAudioTaggingProviderSettings(
            predictions=[("Bark", 0.7), ("Meow", 0.2)],
        )
    )

    result = await provider.predict(np.zeros(1600), 16000, run_context=run_context)

    assert [p.label for p in result] == ["Bark", "Meow"]
    assert [p.score for p in result] == [0.7, 0.2]


async def test_mock_audio_tagging_provider_defaults(run_context: RunContext) -> None:
    provider = MockAudioTaggingProvider(MockAudioTaggingProviderSettings())

    result = await provider.predict(np.zeros(1600), 16000, run_context=run_context)

    assert [p.label for p in result] == ["Speech", "Music", "Silence"]
