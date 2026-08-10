import os
from typing import TypeAlias

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info import AudioFileInfo
from kiarina.agi.file_info_builder import BuildResult, FileInfoSpec
from kiarina.agi.file_utils import normalize_time
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_audio_token
from kiarina.utils.file import FileBlob

from .._utils.encode_mono_16kbps_mp3 import encode_mono_16kbps_mp3
from .._utils.read_audio_metadata import read_audio_metadata

OutputFilePath: TypeAlias = str


async def build_analysis_disabled(
    file_info_spec: FileInfoSpec,
    file_blob: FileBlob,
    *,
    run_context: RunContext,
) -> BuildResult:
    duration = (await read_audio_metadata(file_blob.file_path)).duration

    output_base_path = create_local_repository(run_context).generate_cache_path(
        os.path.join("intermediate", "audio", file_blob.hash_string)
    )

    start_time = normalize_time(file_info_spec.get("start_time", 0.0), duration)
    end_time = normalize_time(file_info_spec.get("end_time", -1.0), duration)

    intermediate_file_path: str | None = None
    intermediate_file_path = _get_output_file_path(
        output_base_path, start_time, end_time, duration
    )

    if not os.path.exists(intermediate_file_path):
        await encode_mono_16kbps_mp3(
            file_blob.file_path,
            intermediate_file_path,
            start_time=start_time,
            end_time=end_time,
        )

        if not _is_optimized(file_blob.file_path, intermediate_file_path):
            os.remove(intermediate_file_path)
            intermediate_file_path = None

    intermediate_file_blob: FileBlob | None = None

    if intermediate_file_path:
        intermediate_file_blob = await kfa.read_file(intermediate_file_path)

    target_blob = intermediate_file_blob or file_blob

    target_metadata = await read_audio_metadata(target_blob.file_path)
    file_size = len(target_blob.raw_data)
    token_count = calc_audio_token(target_metadata.duration)

    return BuildResult(
        file_info=AudioFileInfo.model_validate(
            {
                **file_info_spec,
                # from file_blob
                "mime_type": file_blob.mime_type,
                "file_hash": file_blob.hash_string,
                # from processing
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


def _get_output_file_path(
    output_base_path: str,
    start_time: float,
    end_time: float,
    duration: float,
) -> OutputFilePath:
    if start_time != 0.0 or end_time != duration:
        return f"{output_base_path}_{start_time:.1f}_{end_time:.1f}.mp3"
    else:
        return f"{output_base_path}.mp3"


def _is_optimized(input_file_path: str, output_file_path: str) -> bool:
    return os.path.getsize(output_file_path) < os.path.getsize(input_file_path)
