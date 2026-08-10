import os
from pathlib import Path

import pytest

from kiarina.agi.file_info_builder_impl.audio._utils.read_audio_metadata import (
    read_audio_metadata,
)
from kiarina.agi.file_info_builder_impl.audio._utils.trim_audio import (
    trim_audio,
)


@pytest.mark.parametrize(
    "start_time,end_time",
    [
        pytest.param(0.0, -1.0, id="full_clip"),
        pytest.param(0.5, 1.5, id="partial_clip"),
    ],
)
async def test_trim_audio(
    start_time: float, end_time: float, test_data_dir: Path, tmp_path: Path
) -> None:
    input_file_path = test_data_dir / "mp3" / "tone_2s_16kb.mp3"
    output_file_path = tmp_path / "trimmed.mp3"

    result = await trim_audio(
        input_file_path,
        output_file_path,
        start_time=start_time,
        end_time=end_time,
    )

    assert result == str(output_file_path)
    assert output_file_path.exists()

    input_metadata = await read_audio_metadata(str(input_file_path))
    output_metadata = await read_audio_metadata(str(output_file_path))

    expected_duration = (
        input_metadata.duration if end_time == -1.0 else end_time - start_time
    )

    assert output_metadata.duration == pytest.approx(expected_duration, abs=0.15)

    print(f"output_file_path: file://{output_file_path}")


async def test_trim_audio_full_clip_copies_original(
    test_data_dir: Path, tmp_path: Path
) -> None:
    input_file_path = test_data_dir / "mp3" / "tone_2s_16kb.mp3"
    output_file_path = tmp_path / "trimmed.mp3"

    await trim_audio(input_file_path, output_file_path)

    assert os.path.getsize(output_file_path) == os.path.getsize(input_file_path)
    assert output_file_path.read_bytes() == input_file_path.read_bytes()
    print(f"output_file_path: file://{output_file_path}")


async def test_trim_audio_rejects_empty_range(
    test_data_dir: Path, tmp_path: Path
) -> None:
    with pytest.raises(ValueError, match="start_time must be earlier than end_time"):
        await trim_audio(
            test_data_dir / "mp3" / "tone_2s_16kb.mp3",
            tmp_path / "trimmed.mp3",
            start_time=1.0,
            end_time=1.0,
        )
