from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_model import text_to_speech

pytestmark = [pytest.mark.costly]


async def test_text_to_speech(
    tts_model_name: str, cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    result = await text_to_speech(
        "Hello, this is a test of the text-to-speech functionality.",
        tts_options={"tts_model": tts_model_name},
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print("---- TTS Result ----")
    print(f"Audio saved to: '{result}'")
    print(f"File size: {Path(result).stat().st_size} bytes")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    assert Path(result).stat().st_size > 0


async def test_text_to_speech_with_instructions(
    tts_model_name: str, cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    result = await text_to_speech(
        "Hello, this is a test.",
        tts_options={
            "tts_model": tts_model_name,
            "instructions": "Speak slowly and clearly.",
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print("---- TTS Result with Instructions ----")
    print(f"Audio saved to: '{result}'")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    assert Path(result).stat().st_size > 0
