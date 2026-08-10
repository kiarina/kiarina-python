from collections.abc import Sequence

from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext

from .._types.file_info_input import FileInfoInput
from .load_file_info import load_file_info


async def load_file_infos(
    file_info_inputs: Sequence[FileInfoInput],
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    file_infos: list[FileInfo] = []

    for file_info_input in file_info_inputs:
        if file_info := await load_file_info(file_info_input, run_context=run_context):
            file_infos.append(file_info)

    return file_infos
