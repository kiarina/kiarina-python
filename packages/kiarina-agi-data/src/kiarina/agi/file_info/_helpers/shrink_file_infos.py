from kiarina.agi.token_utils import TokenCount

from .._types.file_info import FileInfo


def shrink_file_infos(
    file_infos: list[FileInfo],
    *,
    reduce: TokenCount,
    reserve: TokenCount = 0,
) -> tuple[list[FileInfo], TokenCount]:
    reduced: TokenCount = 0
    new_file_infos: list[FileInfo] = []

    for file_info in file_infos:
        if reduced >= reduce:
            new_file_infos.append(file_info)
            continue

        new_file_info, new_reduced = file_info.shrink(
            reduce=max(0, reduce - reduced),
            reserve=reserve,
        )

        reduced += new_reduced
        new_file_infos.append(new_file_info)

    return new_file_infos, reduced
