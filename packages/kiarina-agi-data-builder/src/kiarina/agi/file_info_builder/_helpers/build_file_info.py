import json
from typing import cast

from kiarina.agi.file_info import detect_file_type
from kiarina.agi.run_context import RunContext
from kiarina.utils.common import parse_config_string
from kiarina.utils.file import FileBlob

from .._schemas.build_result import BuildResult
from .._services.file_info_builder_registry import file_info_builder_registry
from .._types.file_info_spec import FileInfoSpec
from .._types.file_info_specifier import FileInfoSpecifier


async def build_file_info(
    file_info_spec: FileInfoSpec | FileInfoSpecifier,
    file_blob: FileBlob,
    *,
    run_context: RunContext,
) -> BuildResult:
    if isinstance(file_info_spec, str):
        if file_info_spec.startswith("{"):
            file_info_spec_maybe = json.loads(file_info_spec)

            if "uri_or_file_path" not in file_info_spec_maybe:  # pragma: no cover
                raise ValueError(f"Invalid FileInfoSpec string: {file_info_spec}")

            file_info_spec = cast(FileInfoSpec, file_info_spec_maybe)

        elif "?" in file_info_spec:
            uri_or_file_path, config_string = file_info_spec.split("?", 1)
            config = parse_config_string(
                config_string, separator="&", key_value_separator="="
            )
            file_info_spec = cast(
                FileInfoSpec, {"uri_or_file_path": uri_or_file_path, **config}
            )

        else:
            file_info_spec = cast(FileInfoSpec, {"uri_or_file_path": file_info_spec})

    file_type = detect_file_type(file_blob)
    file_builder = file_info_builder_registry.resolve(file_type)
    return await file_builder.build(file_info_spec, file_blob, run_context=run_context)
