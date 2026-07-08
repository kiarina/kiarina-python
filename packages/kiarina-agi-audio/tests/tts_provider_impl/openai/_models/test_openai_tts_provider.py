from pathlib import Path
from typing import TypedDict

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider_impl.openai import (
    OpenAITTSProvider,
    OpenAITTSProviderSettings,
)


class _TTSKwargs(TypedDict):
    cost_recorder: CostRecorder
    run_context: RunContext


@pytest.fixture
def provider() -> OpenAITTSProvider:
    settings = OpenAITTSProviderSettings()
    provider = OpenAITTSProvider(settings)
    provider.name = "openai"
    return provider


@pytest.fixture
def kwargs(cost_recorder: CostRecorder, run_context: RunContext) -> _TTSKwargs:
    return {
        "cost_recorder": cost_recorder,
        "run_context": run_context,
    }


def test_init_and_properties(provider: OpenAITTSProvider) -> None:
    print(str(provider))
    print(f"openai_settings: {provider.openai_settings}")


def test_output_extension(run_context: RunContext, provider: OpenAITTSProvider) -> None:
    opus_path = provider._generate_cache_path(
        "Hello",
        instructions=None,
        output_format="opus",
        run_context=run_context,
    )

    flac_path = provider._generate_cache_path(
        "Hello",
        instructions=None,
        output_format="flac",
        run_context=run_context,
    )

    assert opus_path.endswith(".ogg")
    assert flac_path.endswith(".flac")


@pytest.mark.parametrize("output_format", ["webm", "pcm"])
async def test_unsupported_output_format(
    run_context: RunContext,
    output_format: str,
) -> None:
    provider = OpenAITTSProvider(OpenAITTSProviderSettings())
    provider.name = "openai"

    with pytest.raises(
        ValueError,
        match=f"Unsupported OpenAI TTS output_format: {output_format}",
    ):
        await provider.text_to_speech(
            "Hello",
            output_format=output_format,
            run_context=run_context,
            ignore_cache=True,
        )


@pytest.mark.costly
async def test_text_to_speech(provider: OpenAITTSProvider, kwargs: _TTSKwargs) -> None:
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
    provider: OpenAITTSProvider, kwargs: _TTSKwargs
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
