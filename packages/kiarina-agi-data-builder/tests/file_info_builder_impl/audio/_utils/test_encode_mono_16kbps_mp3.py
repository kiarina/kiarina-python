import os
from pathlib import Path

import pytest
import soundfile as sf  # type: ignore

from kiarina.agi.file_info_builder_impl.audio._utils.encode_mono_16kbps_mp3 import (
    encode_mono_16kbps_mp3,
)
from kiarina.agi.file_info_builder_impl.audio._utils.read_audio_metadata import (
    read_audio_metadata,
)


async def test_encode_mono_16kbps_mp3(test_data_dir: Path, tmp_path: Path) -> None:
    input_file_path = test_data_dir / "mp3" / "tone_2s_16kb.mp3"
    output_file_path = tmp_path / "encoded.mp3"

    result = await encode_mono_16kbps_mp3(input_file_path, output_file_path)

    assert result == str(output_file_path)
    assert output_file_path.exists()
    assert os.path.getsize(output_file_path) < os.path.getsize(input_file_path)

    input_metadata = await read_audio_metadata(str(input_file_path))
    output_metadata = await read_audio_metadata(str(output_file_path))
    samples, _ = sf.read(output_file_path, always_2d=True)

    assert output_metadata.duration == pytest.approx(input_metadata.duration, abs=0.05)
    assert samples.shape[1] == 1

    print(f"output_file_path: file://{output_file_path}")


async def test_encode_mono_16kbps_mp3_segment(
    test_data_dir: Path, tmp_path: Path
) -> None:
    input_file_path = test_data_dir / "mp3" / "tone_2s_16kb.mp3"
    output_file_path = tmp_path / "encoded.mp3"

    result = await encode_mono_16kbps_mp3(
        input_file_path,
        output_file_path,
        start_time=0.5,
        end_time=1.5,
    )

    assert result == str(output_file_path)
    assert output_file_path.exists()

    output_metadata = await read_audio_metadata(str(output_file_path))
    samples, _ = sf.read(output_file_path, always_2d=True)

    assert output_metadata.duration == pytest.approx(1.0, abs=0.15)
    assert samples.shape[1] == 1
