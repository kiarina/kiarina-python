from abc import ABC, abstractmethod

from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._schemas.build_result import BuildResult
from .._types.file_info_builder import FileInfoBuilder
from .._types.file_info_spec import FileInfoSpec


class BaseFileInfoBuilder(FileInfoBuilder, ABC):
    @abstractmethod
    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult: ...
