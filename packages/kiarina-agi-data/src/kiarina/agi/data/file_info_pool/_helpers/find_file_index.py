from kiarina.agi.data.file_info import FileID

from .._types.file_info_pool import FileInfoPool


def find_file_index(pool: FileInfoPool, file_id: FileID) -> int | None:
    for index, file_info in enumerate(pool):
        if file_info.id == file_id:
            return index

    return None
