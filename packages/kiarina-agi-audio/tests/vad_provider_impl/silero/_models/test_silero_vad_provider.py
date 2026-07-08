import numpy as np

from kiarina.agi.audio_source import audio_source_registry
from kiarina.agi.vad_provider_impl.silero import (
    SileroVADProvider,
    SileroVADProviderSettings,
)


async def test_silero_vad_provider(
    speech_audio_file_path: str, silero_vad_model_path: str
) -> None:
    provider = SileroVADProvider(
        SileroVADProviderSettings(
            model_path=silero_vad_model_path,
        )
    )
    audio_source = audio_source_registry.resolve("file")

    async with audio_source.open(speech_audio_file_path):
        async for chunk in audio_source.read():
            samples = (
                chunk.samples[0]
                if chunk.samples.shape[0] == 1
                else chunk.samples.mean(axis=0)
            )
            speech_prob = await provider.predict(np.asarray(samples), chunk.sample_rate)
            print(f"Speech probability: {speech_prob:.4f}")

    assert True
