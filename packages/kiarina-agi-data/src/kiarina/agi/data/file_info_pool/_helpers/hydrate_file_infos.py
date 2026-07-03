from kiarina.agi.data.file_info import FileInfo

from .._types.file_info_pool import FileInfoPool
from .find_file_index import find_file_index


def hydrate_file_infos(
    file_infos: list[FileInfo],
    pool: FileInfoPool,
) -> tuple[list[FileInfo], FileInfoPool]:
    hydrated = False
    new_file_infos: list[FileInfo] = []

    for file_info in file_infos:
        new_file_info, pool = _hydrate_file_info(file_info, pool)

        if new_file_info is not file_info:
            hydrated = True

        new_file_infos.append(new_file_info)

    if not hydrated:
        return file_infos, pool
    else:
        return new_file_infos, pool


def _hydrate_file_info(
    file_info: FileInfo,
    pool: FileInfoPool,
) -> tuple[FileInfo, FileInfoPool]:
    file_index = find_file_index(pool, file_info.id)

    if file_index is None:
        return file_info, pool

    elif not file_info.metadata_only:
        return file_info, pool

    else:
        pool = pool.copy()
        new_file_info = pool.pop(file_index)

        return new_file_info, pool
