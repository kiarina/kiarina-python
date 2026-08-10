import os
from pathlib import Path

import pytest

from kiarina.agi.file_bundle import FileBundle, FileBundleTextContent
from kiarina.agi.file_info import VideoFileInfo
from kiarina.agi.file_info_builder import FileInfoSpec
from kiarina.agi.file_info_builder_impl.video._operations import (
    build_analysis_enabled as build_analysis_enabled_module,
)
from kiarina.agi.file_info_builder_impl.video._operations.build_analysis_enabled import (
    _get_bundle_file_path,
    build_analysis_enabled,
)
from kiarina.agi.file_info_builder_impl.video._operations.read_video_metadata import (
    read_video_metadata,
)
from kiarina.agi.file_info_builder_impl.video._schemas.video_metadata import (
    VideoMetadata,
)
from kiarina.agi.file_info_builder_impl.video._settings import (
    VideoFileInfoBuilderSettings,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


def _settings() -> VideoFileInfoBuilderSettings:
    return VideoFileInfoBuilderSettings(
        analysis_enabled=True,
        audio_consumers=[],
        audio_event_bundlers=[],
    )


def test_bundle_cache_signature_includes_analysis_inputs() -> None:
    file_path = "/tmp/video.mp4"
    settings = _settings()
    base = _get_bundle_file_path(
        file_path,
        file_info_spec={"uri_or_file_path": file_path},
        settings=settings,
    )
    changed_segment = _get_bundle_file_path(
        file_path,
        file_info_spec={"uri_or_file_path": file_path, "start_time": 1.0},
        settings=settings,
    )
    changed_fps = _get_bundle_file_path(
        file_path,
        file_info_spec={"uri_or_file_path": file_path, "analysis_fps": 2.0},
        settings=settings,
    )
    changed_audio_settings = _get_bundle_file_path(
        file_path,
        file_info_spec={"uri_or_file_path": file_path},
        settings=settings.model_copy(update={"audio_consumers": ["transcription"]}),
    )

    assert len({base, changed_segment, changed_fps, changed_audio_settings}) == 4


async def test_build_analysis_enabled_creates_video_and_frame_blocks(
    run_context: RunContext,
    short_video_file_path: Path,
) -> None:
    file_blob = await read_file(short_video_file_path)
    assert file_blob is not None

    result = await build_analysis_enabled(
        {"uri_or_file_path": file_blob.file_path},
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )

    assert isinstance(result.file_info, VideoFileInfo)
    assert result.file_info.width == 1600
    assert result.file_info.height == 900
    assert result.file_info.fps == 24.0
    assert result.file_info.analysis_fps == 1.0
    assert result.intermediate_file_blob is not None
    assert result.intermediate_file_blob.mime_type == FileBundle.MIME_TYPE

    bundle = FileBundle.from_bytes(result.intermediate_file_blob.raw_data)
    assert bundle.manifest.contents[0].type == "video"
    assert bundle.manifest.contents[0].visibility == "supported"
    assert len(bundle.manifest.contents) == 14
    assert all(
        content.visibility == "unsupported" for content in bundle.manifest.contents[1:]
    )


async def test_build_analysis_enabled_appends_audio_text_blocks(
    monkeypatch: pytest.MonkeyPatch,
    run_context: RunContext,
    short_video_file_path: Path,
) -> None:
    file_blob = await read_file(short_video_file_path)
    assert file_blob is not None

    async def read_video_metadata_with_audio(file_path: str) -> VideoMetadata:
        metadata = await read_video_metadata(file_path)
        return VideoMetadata(
            duration=metadata.duration,
            width=metadata.width,
            height=metadata.height,
            fps=metadata.fps,
            total_frames=metadata.total_frames,
            has_audio_track=True,
        )

    async def build_audio_text_bundle(
        video_file_path: str,
        *,
        settings: VideoFileInfoBuilderSettings,
        run_context: RunContext,
    ) -> FileBundle:
        return FileBundle.create(
            [
                FileBundleTextContent(
                    text="<transcript>speech</transcript>",
                    visibility="unsupported",
                ),
                FileBundleTextContent(
                    text="<ambient>music</ambient>",
                    visibility="unsupported",
                ),
            ]
        )

    monkeypatch.setattr(
        build_analysis_enabled_module,
        "read_video_metadata",
        read_video_metadata_with_audio,
    )
    monkeypatch.setattr(
        build_analysis_enabled_module,
        "_build_audio_text_bundle",
        build_audio_text_bundle,
    )

    result = await build_analysis_enabled(
        {
            "uri_or_file_path": file_blob.file_path,
            "analysis_fps": 0.5,
        },
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )
    assert result.intermediate_file_blob is not None
    bundle = FileBundle.from_bytes(result.intermediate_file_blob.raw_data)
    transcript = bundle.manifest.contents[-2]
    ambient = bundle.manifest.contents[-1]
    assert isinstance(transcript, FileBundleTextContent)
    assert isinstance(ambient, FileBundleTextContent)
    assert transcript.text.startswith("<transcript>")
    assert ambient.text.startswith("<ambient>")


async def test_build_analysis_enabled_reuses_cached_bundle(
    run_context: RunContext,
    short_video_file_path: Path,
) -> None:
    file_blob = await read_file(short_video_file_path)
    assert file_blob is not None
    spec: FileInfoSpec = {
        "uri_or_file_path": file_blob.file_path,
        "analysis_fps": 0.25,
    }

    first = await build_analysis_enabled(
        spec,
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )
    bundle_path = first.file_info.intermediate_file_path
    assert bundle_path is not None
    mtime = os.path.getmtime(bundle_path)

    second = await build_analysis_enabled(
        spec,
        file_blob,
        run_context=run_context,
        settings=_settings(),
    )

    assert second.file_info.intermediate_file_path == bundle_path
    assert os.path.getmtime(bundle_path) == mtime
