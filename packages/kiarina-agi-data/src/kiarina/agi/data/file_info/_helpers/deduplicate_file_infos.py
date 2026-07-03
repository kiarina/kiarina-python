from .._types.file_info import FileInfo


def deduplicate_file_infos(file_infos: list[FileInfo]) -> list[FileInfo]:
    no_unique_key_files = [fi for fi in file_infos if fi.unique_key is None]

    unique_key_files = [fi for fi in file_infos if fi.unique_key is not None]
    unique_key_map: dict[str, FileInfo] = {}

    for file_info in unique_key_files:
        unique_key = file_info.unique_key or ""

        if unique_key not in unique_key_map:
            unique_key_map[unique_key] = file_info
        elif file_info.created_at >= unique_key_map[unique_key].created_at:
            unique_key_map[unique_key] = file_info

    new_file_infos = no_unique_key_files + list(unique_key_map.values())
    new_file_infos.sort(key=lambda fi: fi.created_at)

    return new_file_infos
