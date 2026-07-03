from kiarina.agi.file_info import FileInfo

from .._types.file_info_pool import FileInfoPool


def dehydrate_file_infos(
    file_infos: list[FileInfo],
    pool: FileInfoPool,
) -> tuple[list[FileInfo], FileInfoPool]:
    dehydrated = False
    new_file_infos: list[FileInfo] = []

    for file_info in file_infos:
        new_file_info, pool = _dehydrate_file_info(file_info, pool)

        if new_file_info is not file_info:
            dehydrated = True

        new_file_infos.append(new_file_info)

    if not dehydrated:
        return file_infos, pool
    else:
        return new_file_infos, pool


def _dehydrate_file_info(
    file_info: FileInfo,
    pool: FileInfoPool,
) -> tuple[FileInfo, FileInfoPool]:
    if file_info.metadata_only or file_info.inline:
        return file_info, pool
    else:
        pool = pool.copy()
        pool.append(file_info)
        return file_info.as_metadata_only(), pool
