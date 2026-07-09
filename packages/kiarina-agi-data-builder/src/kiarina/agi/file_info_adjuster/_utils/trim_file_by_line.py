from kiarina.agi.file_info import TextFileInfo
from kiarina.agi.file_info_builder import rebuild_file_info
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


async def trim_file_by_line(
    *,
    file_info: TextFileInfo,
    file_blob: FileBlob,
    keep_line_count: int,
    run_context: RunContext,
) -> TextFileInfo:
    start_line = file_info.normalized_start_line
    end_line = file_info.normalized_end_line
    line_count = file_blob.raw_text.count("\n") + 1

    if file_info.keep_from_end:
        new_start_line = max(end_line - keep_line_count + 1, start_line)
        new_end_line = end_line
    else:
        new_start_line = start_line
        new_end_line = min(start_line + keep_line_count - 1, end_line)

    file = await rebuild_file_info(
        file_info,
        file_blob,
        update={
            "start_line": new_start_line,
            "end_line": new_end_line if new_end_line != line_count else -1,
        },
        run_context=run_context,
    )
    assert isinstance(file.file_info, TextFileInfo)
    return file.file_info
