from collections.abc import Mapping
from typing import Any, cast

from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._schemas.build_result import BuildResult
from .._types.file_info_spec import FileInfoSpec
from .build_file_info import build_file_info


async def rebuild_file_info(
    file_info: FileInfo,
    file_blob: FileBlob,
    *,
    update: Mapping[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult:
    spec = cast(FileInfoSpec, file_info.export())

    if update:
        spec = cast(FileInfoSpec, {**spec, **update})

    return await build_file_info(spec, file_blob, run_context=run_context)
