from pathlib import Path
from types import SimpleNamespace
from typing import Any, TypedDict, cast

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import OutputFormat
from kiarina.agi.tts_provider_impl.google import (
    GoogleTTSProvider,
    GoogleTTSProviderSettings,
)
from kiarina.agi.tts_provider_impl.google._models.google_tts_provider import _save_audio


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


@pytest.mark.parametrize(
    ("output_format", "suffix"),
    [("aac", ".aac"), ("wav", ".wav")],
)
def test_save_audio(
    tmp_path: Path,
    output_format: OutputFormat,
    suffix: str,
) -> None:
    response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(
                    parts=[
                        SimpleNamespace(
                            inline_data=SimpleNamespace(data=b"\0\0" * 2400)
                        )
                    ]
                )
            )
        ]
    )
    output_file_path = tmp_path / f"output{suffix}"

    _save_audio(cast(Any, response), output_format, str(output_file_path))

    assert output_file_path.stat().st_size > 0
