from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._operations.create_file_segment_normalizer import create_file_segment_normalizer


async def normalize_file_segments(
    file_infos: list[FileInfo],
    file_blobs: dict[URIOrFilePath, FileBlob],
    *,
    run_context: RunContext,
) -> list[FileInfo]:
    segments_map = _create_segments_map(file_infos)

    new_file_infos: list[FileInfo] = []

    for uri_or_file_path, segments in segments_map.items():
        normalized_segments = await _normalize_file_segments(
            segments,
            file_blobs[uri_or_file_path],
            run_context,
        )
        new_file_infos.extend(normalized_segments)

    new_file_infos.sort(key=lambda x: x.created_at)

    return new_file_infos


def _create_segments_map(
    file_infos: list[FileInfo],
) -> dict[URIOrFilePath, list[FileInfo]]:
    segments_map: dict[URIOrFilePath, list[FileInfo]] = {}

    for file_info in file_infos:
        uri_or_file_path = file_info.uri_or_file_path

        if uri_or_file_path not in segments_map:
            segments_map[uri_or_file_path] = []

        segments_map[uri_or_file_path].append(file_info)

    return segments_map


async def _normalize_file_segments(
    file_infos: list[FileInfo],
    file_blob: FileBlob,
    run_context: RunContext,
) -> list[FileInfo]:
    metadata_only_file_info: FileInfo | None = None
    actual_file_infos: list[FileInfo] = []

    for file_info in file_infos:
        if file_info.metadata_only:
            if not metadata_only_file_info:
                metadata_only_file_info = file_info
            elif file_info.created_at > metadata_only_file_info.created_at:
                metadata_only_file_info = file_info
        else:
            actual_file_infos.append(file_info)

    # Only metadata_only file info
    if not actual_file_infos:
        if not metadata_only_file_info:  # pragma: no cover
            raise AssertionError("not reachable")

        return [metadata_only_file_info]

    # Only 1 actual file info
    if len(actual_file_infos) == 1:
        return actual_file_infos

    # Multiple actual file infos, normalize segments
    file_type = actual_file_infos[0].type
    normalizer = create_file_segment_normalizer(file_type, run_context=run_context)
    return await normalizer.normalize_file_segments(actual_file_infos, file_blob)
