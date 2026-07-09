from pathlib import Path

from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def test_video_file_info_builder(
    run_context: RunContext, video_file_path: Path
) -> None:
    file_blob = await read_file(video_file_path)
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )

    print("VideoFileInfo:")
    print(file.file_info.model_dump_json(indent=2))
