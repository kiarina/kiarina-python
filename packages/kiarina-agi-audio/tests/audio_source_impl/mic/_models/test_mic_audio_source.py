import pytest

from kiarina.agi.audio_source_impl.mic import (
    MicAudioSource,
    MicAudioSourceSettings,
)


@pytest.mark.skip(reason="Requires microphone access and sounddevice library")
async def test_mic_audio_source() -> None:
    audio_source = MicAudioSource(MicAudioSourceSettings())
    print(f"__str__: {audio_source}")

    async with audio_source.open(None):
        async for chunk in audio_source.read():
            print(
                f"chunk: {chunk.samples.shape} {chunk.samples.dtype} {chunk.sample_rate}"
            )
            break

    assert True
