from typing import Protocol, runtime_checkable

from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._schemas.build_result import BuildResult
from .file_info_spec import FileInfoSpec


@runtime_checkable
class FileInfoBuilder(Protocol):
    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult: ...
