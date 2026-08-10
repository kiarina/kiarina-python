from pathlib import Path

from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def test_build_file_info(run_context: RunContext, test_data_dir: Path) -> None:
    file_blob = await read_file(str(test_data_dir / "txt" / "hello_world_11b.txt"))
    assert file_blob is not None

    result = await build_file_info(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
    )
    assert result.file_info.uri_or_file_path == file_blob.file_path

    result = await build_file_info(
        str(file_blob.file_path),
        file_blob,
        run_context=run_context,
    )
    assert result.file_info.uri_or_file_path == file_blob.file_path

    result = await build_file_info(
        f"{file_blob.file_path}?group=hello",
        file_blob,
        run_context=run_context,
    )
    assert result.file_info.uri_or_file_path == file_blob.file_path

    result = await build_file_info(
        f'{{"uri_or_file_path": "{file_blob.file_path}", "group": "hello"}}',
        file_blob,
        run_context=run_context,
    )
    assert result.file_info.uri_or_file_path == file_blob.file_path

    print(result.file_info.model_dump_json(indent=2))
