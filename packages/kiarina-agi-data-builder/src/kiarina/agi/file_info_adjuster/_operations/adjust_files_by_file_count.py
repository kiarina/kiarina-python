from kiarina.agi.file_info import FileInfo, FileType


def adjust_files_by_file_count(
    file_infos: list[FileInfo],
    target_file_type: FileType,
    file_count_limit: int,
) -> list[FileInfo]:
    if file_count_limit == -1:
        return file_infos

    target_file_infos = [
        file_info for file_info in file_infos if file_info.type == target_file_type
    ]

    target_file_infos.sort(key=lambda fi: -fi.created_at.timestamp())

    remove_ids = [file_info.id for file_info in target_file_infos[file_count_limit:]]

    if not remove_ids:
        return file_infos

    new_file_infos = [
        file_info for file_info in file_infos if file_info.id not in remove_ids
    ]

    new_file_infos.sort(key=lambda fi: fi.created_at)

    return new_file_infos
