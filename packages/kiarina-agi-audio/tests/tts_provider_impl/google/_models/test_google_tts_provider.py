from pathlib import Path
from typing import TypedDict

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider_impl.google import (
    GoogleTTSProvider,
    GoogleTTSProviderSettings,
)


class _TTSKwargs(TypedDict):
    cost_recorder: CostRecorder
    run_context: RunContext


@pytest.fixture
def provider() -> GoogleTTSProvider:
    settings = GoogleTTSProviderSettings()
    provider = GoogleTTSProvider(settings)
    provider.name = "google"
    return provider


@pytest.fixture
def kwargs(cost_recorder: CostRecorder, run_context: RunContext) -> _TTSKwargs:
    return {
        "cost_recorder": cost_recorder,
        "run_context": run_context,
    }


def test_init_and_properties(provider: GoogleTTSProvider) -> None:
    print(str(provider))
    print(f"google_auth_settings: {provider.google_auth_settings}")
    print(f"credentials: {provider.credentials}")
    print(f"client: {provider.client}")


@pytest.mark.costly
async def test_text_to_speech(provider: GoogleTTSProvider, kwargs: _TTSKwargs) -> None:
    result = await provider.text_to_speech(
        "Hello, this is a test of the text-to-speech functionality.",
        output_format="wav",
        **kwargs,
    )

    print("---- TTS Result ----")
    print(f"Audio saved to: '{result}'")
    print(f"File size: {Path(result).stat().st_size} bytes")

    assert Path(result).stat().st_size > 0


@pytest.mark.costly
async def test_text_to_speech_with_instructions(
    provider: GoogleTTSProvider, kwargs: _TTSKwargs
) -> None:
    result = await provider.text_to_speech(
        "Hello, this is a test of the text-to-speech functionality.",
        instructions="Speak slowly and clearly.",
        output_format="wav",
        **kwargs,
    )

    print("---- TTS Result with Instructions ----")
    print(f"Audio saved to: '{result}'")

    assert Path(result).stat().st_size > 0


@pytest.mark.costly
async def test_multi_speaker(provider: GoogleTTSProvider, kwargs: _TTSKwargs) -> None:
    provider.settings.speakers = {
        "Alice": "Zephyr",
        "Bob": "Charon",
    }

    prompt = """
TTS the following conversation between Alice and Bob:
Alice: How's it going today Bob?
Bob: Not too bad, how about you?
    """.strip()

    result = await provider.text_to_speech(
        prompt,
        output_format="wav",
        **kwargs,
    )

    print("---- TTS Result with Instructions ----")
    print(f"Audio saved to: '{result}'")

    assert Path(result).stat().st_size > 0
