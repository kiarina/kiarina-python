from kiarina.agi.file_info_builder import (
    BaseFileInfoBuilder,
    BuildResult,
    FileInfoSpec,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._operations.build_analysis_disabled import build_analysis_disabled
from .._operations.build_analysis_enabled import build_analysis_enabled
from .._settings import AudioFileInfoBuilderSettings


class AudioFileInfoBuilder(BaseFileInfoBuilder):
    def __init__(self, settings: AudioFileInfoBuilderSettings) -> None:
        self.settings: AudioFileInfoBuilderSettings = settings

    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult:
        if self.settings.analysis_enabled:
            return await build_analysis_enabled(
                file_info_spec,
                file_blob,
                run_context=run_context,
                settings=self.settings,
            )

        return await build_analysis_disabled(
            file_info_spec,
            file_blob,
            run_context=run_context,
        )
