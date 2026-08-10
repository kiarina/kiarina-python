import sys
from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.asr_provider_impl.command import (
    CommandASRProvider,
    CommandASRProviderSettings,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.run_context import RunContext


def _samples() -> MonoSamples:
    return np.asarray([0.0, 0.5, -0.5], dtype=np.float32)


async def test_speech_to_text_file_mode(run_context: RunContext) -> None:
    provider = CommandASRProvider(
        CommandASRProviderSettings(
            text_command_args=[
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "assert Path('{input_file}').exists(); "
                    "Path('{output_file}').write_text('hello', encoding='utf-8')"
                ),
            ],
        )
    )

    text = await provider.speech_to_text(
        _samples(),
        16_000,
        run_context=run_context,
    )

    assert text == "hello"


async def test_speech_to_text_stdin_mode(run_context: RunContext) -> None:
    provider = CommandASRProvider(
        CommandASRProviderSettings(
            text_command_args=[
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "from pathlib import Path; "
                    "data = sys.stdin.buffer.read(); "
                    "assert data.startswith(b'RIFF'); "
                    "Path('{output_file}').write_text('stdin ok', encoding='utf-8')"
                ),
            ],
            text_command_input_mode="stdin",
        )
    )

    text = await provider.speech_to_text(
        _samples(),
        16_000,
        run_context=run_context,
    )

    assert text == "stdin ok"


async def test_speech_to_segments(run_context: RunContext, tmp_path: Path) -> None:
    srt_file_path = tmp_path / "source.srt"
    srt_file_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,250\n[Speaker 1] hello\n",
        encoding="utf-8",
    )

    provider = CommandASRProvider(
        CommandASRProviderSettings(
            segments_command_args=[
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    f"Path({str(srt_file_path)!r}).replace('{{output_file}}')"
                ),
            ],
        )
    )

    segments = await provider.speech_to_segments(
        _samples(),
        16_000,
        run_context=run_context,
    )

    assert len(segments) == 1
    assert segments[0].text == "hello"
    assert segments[0].start_timestamp == 0.0
    assert segments[0].end_timestamp == 1.25
    assert segments[0].metadata["speaker_name"] == "Speaker 1"


async def test_speech_to_segments_stdin_mode(run_context: RunContext) -> None:
    provider = CommandASRProvider(
        CommandASRProviderSettings(
            segments_command_input_mode="stdin",
            segments_command_args=[
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "from pathlib import Path; "
                    "data = sys.stdin.buffer.read(); "
                    "assert data.startswith(b'RIFF'); "
                    "Path('{output_file}').write_text("
                    "'1\\n00:00:00,000 --> 00:00:01,250\\nhello\\n', "
                    "encoding='utf-8')"
                ),
            ],
        )
    )

    segments = await provider.speech_to_segments(
        _samples(),
        16_000,
        run_context=run_context,
    )

    assert len(segments) == 1
    assert segments[0].text == "hello"


async def test_timed_out(run_context: RunContext) -> None:
    provider = CommandASRProvider(
        CommandASRProviderSettings(
            text_command_args=[sys.executable, "-c", "import time; time.sleep(1)"],
            timeout=0.1,
        )
    )

    with pytest.raises(TimeoutError, match="Timed out"):
        await provider.speech_to_text(_samples(), 16_000, run_context=run_context)


async def test_failed(run_context: RunContext) -> None:
    provider = CommandASRProvider(
        CommandASRProviderSettings(text_command_args=[sys.executable, "-c", "exit(1)"])
    )

    with pytest.raises(RuntimeError, match="Failed with exit code"):
        await provider.speech_to_text(_samples(), 16_000, run_context=run_context)


async def test_did_not_create(run_context: RunContext) -> None:
    provider = CommandASRProvider(
        CommandASRProviderSettings(text_command_args=[sys.executable, "-c", "pass"])
    )

    with pytest.raises(RuntimeError, match="Did not create output file"):
        await provider.speech_to_text(_samples(), 16_000, run_context=run_context)


async def test_unknown_command_placeholder(run_context: RunContext) -> None:
    provider = CommandASRProvider(
        CommandASRProviderSettings(
            text_command_args=["{unknown_placeholder}"],
        )
    )

    with pytest.raises(ValueError, match="Unknown command placeholder"):
        await provider.speech_to_text(_samples(), 16_000, run_context=run_context)
