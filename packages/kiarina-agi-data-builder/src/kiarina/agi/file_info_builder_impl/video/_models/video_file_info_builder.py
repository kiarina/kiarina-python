import os

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info import VideoFileInfo
from kiarina.agi.file_info_builder import (
    BaseFileInfoBuilder,
    BuildResult,
    FileInfoSpec,
)
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_video_token
from kiarina.utils.file import FileBlob

from .._operations.build_intermediate_video import build_intermediate_video
from .._operations.read_video_metadata import read_video_metadata


class VideoFileInfoBuilder(BaseFileInfoBuilder):
    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult:
        video_metadata = await read_video_metadata(file_blob.file_path)
        duration = video_metadata.duration

        output_base_path = create_local_repository(run_context).generate_cache_path(
            os.path.join("intermediate", "video", file_blob.hash_string)
        )

        intermediate_file_path = await build_intermediate_video(
            file_blob.file_path,
            output_base_path,
            start_time=file_info_spec.get("start_time", 0.0),
            end_time=file_info_spec.get("end_time", -1.0),
        )

        intermediate_file_blob: FileBlob | None = None

        if intermediate_file_path:
            intermediate_file_blob = await kfa.read_file(intermediate_file_path)

        target_blob = intermediate_file_blob or file_blob

        target_metadata = await read_video_metadata(target_blob.file_path)
        file_size = len(target_blob.raw_data)
        token_count = calc_video_token(target_metadata.duration)

        return BuildResult(
            file_info=VideoFileInfo.model_validate(
                {
                    **file_info_spec,
                    # from file_blob
                    "mime_type": file_blob.mime_type,
                    "file_hash": file_blob.hash_string,
                    # from processing
                    "width": target_metadata.width,
                    "height": target_metadata.height,
                    "duration": duration,
                    "file_size": file_size,
                    "token_count": token_count,
                    "intermediate_file_path": intermediate_file_path,
                    "asset_uri": None,
                }
            ),
            file_blob=file_blob,
            intermediate_file_blob=intermediate_file_blob,
        )
