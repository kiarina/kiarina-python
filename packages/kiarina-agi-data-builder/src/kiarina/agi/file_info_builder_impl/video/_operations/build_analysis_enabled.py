import os
from hashlib import sha1

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleContentInput,
    FileBundleMediaContent,
    FileBundleTextContent,
)
from kiarina.agi.file_info import VideoFileInfo
from kiarina.agi.file_info_builder import BuildResult, FileInfoSpec
from kiarina.agi.file_info_builder_impl.audio import (
    AudioFileInfoBuilder,
    AudioFileInfoBuilderSettings,
)
from kiarina.agi.file_utils import normalize_time
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_video_token
from kiarina.utils.file import FileBlob

from .._schemas.video_metadata import VideoMetadata
from .._settings import VideoFileInfoBuilderSettings
from .build_frame_bundle import build_frame_bundle
from .build_intermediate_video import build_intermediate_video
from .extract_audio_track import extract_audio_track
from .read_video_metadata import read_video_metadata

BUNDLE_VERSION = 1


async def build_analysis_enabled(
    file_info_spec: FileInfoSpec,
    file_blob: FileBlob,
    *,
    run_context: RunContext,
    settings: VideoFileInfoBuilderSettings,
) -> BuildResult:
    source_metadata = await read_video_metadata(file_blob.file_path)
    analysis_fps = file_info_spec.get("analysis_fps", 1.0)
    output_base_path = create_local_repository(run_context).generate_cache_path(
        os.path.join("intermediate", "video", file_blob.hash_string)
    )

    intermediate_video_path = await build_intermediate_video(
        file_blob.file_path,
        output_base_path,
        start_time=file_info_spec.get("start_time", 0.0),
        end_time=file_info_spec.get("end_time", -1.0),
        analysis_fps=analysis_fps,
        keep_larger=True,
    )

    if intermediate_video_path is None:  # pragma: no cover
        raise RuntimeError("Failed to build the intermediate video.")

    intermediate_video_blob = await kfa.read_file(intermediate_video_path)

    if intermediate_video_blob is None:
        raise FileNotFoundError(intermediate_video_path)

    bundle_file_path = _get_bundle_file_path(
        output_base_path,
        file_info_spec=file_info_spec,
        settings=settings,
    )
    bundle_file_blob = await kfa.read_file(bundle_file_path)

    if bundle_file_blob is None:
        bundle = _build_video_bundle(intermediate_video_blob)
        bundle += await build_frame_bundle(
            intermediate_video_path,
            analysis_fps=analysis_fps,
        )

        if source_metadata.has_audio_track:
            bundle += await _build_audio_text_bundle(
                intermediate_video_path,
                settings=settings,
                run_context=run_context,
            )

        bundle_raw_data = bundle.to_bytes()
        await kfa.write_binary(bundle_file_path, bundle_raw_data)
        bundle_file_blob = FileBlob(
            bundle_file_path,
            mime_type=FileBundle.MIME_TYPE,
            raw_data=bundle_raw_data,
        )

    start_time = normalize_time(
        file_info_spec.get("start_time", 0.0), source_metadata.duration
    )
    end_time = normalize_time(
        file_info_spec.get("end_time", -1.0), source_metadata.duration
    )

    return _build_result(
        file_info_spec,
        file_blob,
        bundle_file_blob,
        source_metadata=source_metadata,
        analysis_fps=analysis_fps,
        segment_duration=end_time - start_time,
    )


def _build_video_bundle(video_file_blob: FileBlob) -> FileBundle:
    video_file_path = "video.mp4"
    return FileBundle.create(
        manifest_contents=[
            FileBundleMediaContent(
                type="video",
                file_path=video_file_path,
                mime_type=video_file_blob.mime_type,
                visibility="supported",
            )
        ],
        files={video_file_path: video_file_blob.raw_data},
    )


async def _build_audio_text_bundle(
    video_file_path: str,
    *,
    settings: VideoFileInfoBuilderSettings,
    run_context: RunContext,
) -> FileBundle:
    audio_file_path = f"{os.path.splitext(video_file_path)[0]}.audio.mp3"
    await extract_audio_track(video_file_path, audio_file_path)
    audio_file_blob = await kfa.read_file(audio_file_path)

    if audio_file_blob is None:
        raise FileNotFoundError(audio_file_path)

    audio_builder = AudioFileInfoBuilder(
        AudioFileInfoBuilderSettings(
            analysis_enabled=True,
            audio_source=settings.audio_source,
            audio_consumers=settings.audio_consumers,
            audio_event_bundlers=settings.audio_event_bundlers,
        )
    )
    audio_result = await audio_builder.build(
        {"uri_or_file_path": audio_file_path},
        audio_file_blob,
        run_context=run_context,
    )

    if audio_result.intermediate_file_blob is None:
        return FileBundle()

    audio_bundle = FileBundle.from_bytes(audio_result.intermediate_file_blob.raw_data)
    text_contents: list[FileBundleContentInput] = [
        content.model_copy(update={"visibility": "unsupported"})
        for content in audio_bundle.manifest.contents
        if isinstance(content, FileBundleTextContent)
    ]
    return FileBundle.create(manifest_contents=text_contents)


def _get_bundle_file_path(
    output_base_path: str,
    *,
    file_info_spec: FileInfoSpec,
    settings: VideoFileInfoBuilderSettings,
) -> str:
    signature_source = {
        "bundle_version": BUNDLE_VERSION,
        "start_time": file_info_spec.get("start_time", 0.0),
        "end_time": file_info_spec.get("end_time", -1.0),
        "analysis_fps": file_info_spec.get("analysis_fps", 1.0),
        "settings": settings.model_dump(mode="json"),
    }
    signature = sha1(
        repr(sorted(signature_source.items())).encode("utf-8")
    ).hexdigest()[:12]
    return f"{output_base_path}_analysis_{signature}.zip"


def _build_result(
    file_info_spec: FileInfoSpec,
    file_blob: FileBlob,
    bundle_file_blob: FileBlob,
    *,
    source_metadata: VideoMetadata,
    analysis_fps: float,
    segment_duration: float,
) -> BuildResult:
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
                "file_size": len(bundle_file_blob.raw_data),
                "token_count": calc_video_token(segment_duration),
                "intermediate_file_path": bundle_file_blob.file_path,
                "asset_uri": None,
            }
        ),
        file_blob=file_blob,
        intermediate_file_blob=bundle_file_blob,
    )
