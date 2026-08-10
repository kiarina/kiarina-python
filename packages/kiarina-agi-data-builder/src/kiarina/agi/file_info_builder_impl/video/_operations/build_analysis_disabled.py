import os

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info import VideoFileInfo
from kiarina.agi.file_info_builder import BuildResult, FileInfoSpec
from kiarina.agi.file_utils import normalize_time
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_video_token
from kiarina.utils.file import FileBlob

from .build_intermediate_video import build_intermediate_video
from .read_video_metadata import read_video_metadata


async def build_analysis_disabled(
    file_info_spec: FileInfoSpec,
    file_blob: FileBlob,
    *,
    run_context: RunContext,
) -> BuildResult:
    source_metadata = await read_video_metadata(file_blob.file_path)
    analysis_fps = file_info_spec.get("analysis_fps", 1.0)

    output_base_path = create_local_repository(run_context).generate_cache_path(
        os.path.join("intermediate", "video", file_blob.hash_string)
    )

    intermediate_file_path = await build_intermediate_video(
        file_blob.file_path,
        output_base_path,
        start_time=file_info_spec.get("start_time", 0.0),
        end_time=file_info_spec.get("end_time", -1.0),
        analysis_fps=analysis_fps,
    )

    intermediate_file_blob: FileBlob | None = None

    if intermediate_file_path:
        intermediate_file_blob = await kfa.read_file(intermediate_file_path)

    target_blob = intermediate_file_blob or file_blob
    start_time = normalize_time(
        file_info_spec.get("start_time", 0.0), source_metadata.duration
    )
    end_time = normalize_time(
        file_info_spec.get("end_time", -1.0), source_metadata.duration
    )

    return BuildResult(
        file_info=VideoFileInfo.model_validate(
            {
                **file_info_spec,
                "mime_type": file_blob.mime_type,
                "file_hash": file_blob.hash_string,
                "width": source_metadata.width,
                "height": source_metadata.height,
                "fps": source_metadata.fps,
                "analysis_fps": analysis_fps,
                "duration": source_metadata.duration,
                "file_size": len(target_blob.raw_data),
                "token_count": calc_video_token(end_time - start_time),
                "intermediate_file_path": intermediate_file_path,
                "asset_uri": None,
            }
        ),
        file_blob=file_blob,
        intermediate_file_blob=intermediate_file_blob,
    )
