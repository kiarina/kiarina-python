from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._utils.trim_file_by_token import trim_file_by_token


async def adjust_files_by_token_count(
    file_infos: list[FileInfo],
    file_blobs: dict[URIOrFilePath, FileBlob],
    token_count_limit: int,
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    if token_count_limit == -1:
        return file_infos

    file_infos.sort(key=lambda fi: -fi.created_at.timestamp())

    new_file_infos: list[FileInfo] = []
    total_token_count = 0

    for file_info in file_infos:
        token_count = file_info.token_count

        if total_token_count + token_count <= token_count_limit:
            new_file_infos.append(file_info)
            total_token_count += token_count
            continue

        remaining_token_count = token_count_limit - total_token_count

        if remaining_token_count > 0:
            new_file_info = await trim_file_by_token(
                file_info=file_info,
                file_blob=file_blobs[file_info.uri_or_file_path],
                keep_token_count=remaining_token_count,
                run_context=run_context,
            )

            if new_file_info:
                new_file_infos.append(new_file_info)

        break

    new_file_infos.sort(key=lambda fi: fi.created_at)

    return new_file_infos
