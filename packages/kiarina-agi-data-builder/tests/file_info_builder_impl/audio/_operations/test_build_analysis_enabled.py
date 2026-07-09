import json
import os
import re
import zipfile
from pathlib import Path

import pytest

from kiarina.agi.file_info import AudioFileInfo
from kiarina.agi.file_info_builder_impl.audio._operations.build_analysis_enabled import (
    build_analysis_enabled,
)
from kiarina.agi.file_info_builder_impl.audio._settings import (
    AudioFileInfoBuilderSettings,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


def _make_settings(**overrides: object) -> AudioFileInfoBuilderSettings:
    base = {
        "analysis_enabled": True,
        "audio_source": "file?sample_rate=16000&start_timestamp=0.0",
        "audio_consumers": [
            "stt"
            "?vad_model=(mock?sample_rate=16000&speech_probabilities.0=1.0&repeat_last=true)"
            "&scd_model=(mock?default_probability=1.0)"
            "&asr_model=(mock?result_text=mock transcript from op)"
        ],
        "audio_event_bundlers": ["stt"],
    }
    base.update(overrides)
    return AudioFileInfoBuilderSettings.model_validate(base)


async def test_build_analysis_enabled_creates_bundle(
    run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None

    result = await build_analysis_enabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        settings=_make_settings(),
        run_context=run_context,
    )

    assert isinstance(result.file_info, AudioFileInfo)
    assert result.file_info.file_hash == file_blob.hash_string
    assert result.file_info.duration == pytest.approx(2.04, abs=0.1)
    assert result.file_info.token_count > 0

    bundle_path = result.file_info.intermediate_file_path
    assert bundle_path is not None
    assert bundle_path.endswith(".zip")
    assert result.intermediate_file_blob is not None
    assert result.intermediate_file_blob.mime_type == "application/zip"
    assert result.file_info.file_size == len(result.intermediate_file_blob.raw_data)

    with zipfile.ZipFile(bundle_path) as zip_file:
        manifest = json.loads(zip_file.read("manifest.json").decode("utf-8"))
        audio_data = zip_file.read("audio.mp3")

    assert audio_data
    assert manifest["contents"][0]["file_path"] == "audio.mp3"
    transcript = manifest["contents"][1]["text"]
    assert "mock transcript from op" in transcript
    assert transcript.startswith("<transcript>")
    assert transcript.endswith("</transcript>")
    # SRT format: each entry is "index\nHH:MM:SS,mmm --> HH:MM:SS,mmm\ntext".
    matches = re.findall(
        r"^(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> \d{2}:\d{2}:\d{2},\d{3}$",
        transcript,
        flags=re.MULTILINE,
    )
    assert matches, transcript
    # start_timestamp=0.0 means transcript timestamps are file-relative (hours == 0).
    for hours, *_ in matches:
        assert hours == "00", f"Expected file-relative timestamp, got hours={hours}"

    print(f"transcript: {transcript}")


async def test_build_analysis_enabled_caches_bundle(
    run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None
    settings = _make_settings()

    first = await build_analysis_enabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        settings=settings,
        run_context=run_context,
    )
    bundle_path = first.file_info.intermediate_file_path
    assert bundle_path is not None
    mtime_before = os.path.getmtime(bundle_path)

    second = await build_analysis_enabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        settings=settings,
        run_context=run_context,
    )

    assert second.file_info.intermediate_file_path == bundle_path
    assert os.path.getmtime(bundle_path) == mtime_before


async def test_build_analysis_enabled_segment_bundle_signature_differs(
    run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await read_file(str(test_data_dir / "mp3" / "tone_2s_16kb.mp3"))
    assert file_blob is not None
    settings = _make_settings()

    full = await build_analysis_enabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        settings=settings,
        run_context=run_context,
    )
    segment = await build_analysis_enabled(
        {
            "uri_or_file_path": file_blob.file_path,
            "start_time": 0.5,
            "end_time": 1.5,
        },
        file_blob,
        settings=settings,
        run_context=run_context,
    )

    assert isinstance(full.file_info, AudioFileInfo)
    assert isinstance(segment.file_info, AudioFileInfo)
    assert (
        full.file_info.intermediate_file_path
        != segment.file_info.intermediate_file_path
    )
    assert segment.file_info.duration == pytest.approx(2.04, abs=0.1)
    # token_count reflects the trimmed (~1s) duration, not the full file.
    assert segment.file_info.token_count < full.file_info.token_count
