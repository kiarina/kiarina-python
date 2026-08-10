import json

from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext

from .._types.file_info_input import FileInfoInput


async def load_file_info(
    file_info_input: FileInfoInput,
    *,
    run_context: RunContext,
) -> FileInfo | None:
    if isinstance(file_info_input, FileInfo):
        return file_info_input

    if isinstance(file_info_input, str):
        if file_info_input.startswith("{"):
            file_info_spec_maybe = json.loads(file_info_input)

            if "uri_or_file_path" not in file_info_spec_maybe:  # pragma: no cover
                raise ValueError(f"Invalid FileInfoSpec string: {file_info_input}")

            uri_or_file_path = file_info_spec_maybe["uri_or_file_path"]

        elif "?" in file_info_input:
            uri_or_file_path, _ = file_info_input.split("?", 1)

        else:
            uri_or_file_path = file_info_input

    else:
        uri_or_file_path = file_info_input["uri_or_file_path"]

    file_blob = await get_file_blob(uri_or_file_path, run_context=run_context)

    if not file_blob:
        return None

    built_file = await build_file_info(
        file_info_input,
        file_blob,
        run_context=run_context,
    )

    return built_file.file_info
