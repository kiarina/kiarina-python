from kiarina.agi.file_info import OtherFileInfo
from kiarina.agi.file_info_builder import (
    BaseFileInfoBuilder,
    BuildResult,
    FileInfoSpec,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob


class OtherFileInfoBuilder(BaseFileInfoBuilder):
    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult:
        return BuildResult(
            file_info=OtherFileInfo.model_validate(
                {
                    **file_info_spec,
                    # from file_blob
                    "mime_type": file_blob.mime_type,
                    "file_hash": file_blob.hash_string,
                    "file_size": len(file_blob.raw_data),
                    # from processing
                    "token_count": 0,
                    "intermediate_file_path": None,
                    "asset_uri": None,
                }
            ),
            file_blob=file_blob,
        )
