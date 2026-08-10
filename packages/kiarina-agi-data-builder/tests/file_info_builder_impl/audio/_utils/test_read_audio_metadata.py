from pathlib import Path

from kiarina.agi.file_info_builder_impl.audio._utils.read_audio_metadata import (
    read_audio_metadata,
)


async def test_read_audio_metadata(test_data_dir: Path) -> None:
    file_path = test_data_dir / "mp3/tone_2s_16kb.mp3"
    metadata = await read_audio_metadata(file_path)
    print(f"metadata: {metadata}")
