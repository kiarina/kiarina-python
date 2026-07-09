import os
from functools import reduce
from hashlib import sha1

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.audio_consumer import AudioEvent, audio_consumer_registry
from kiarina.agi.audio_event_bundler import (
    audio_event_bundler_registry,
)
from kiarina.agi.audio_source import audio_source_registry
from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleMediaContent,
)
from kiarina.agi.file_info import AudioFileInfo
from kiarina.agi.file_info_builder import BuildResult, FileInfoSpec
from kiarina.agi.file_utils import normalize_time
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_audio_token
from kiarina.utils.file import FileBlob

from .._settings import AudioFileInfoBuilderSettings
from .._utils.encode_mono_16kbps_mp3 import encode_mono_16kbps_mp3
from .._utils.read_audio_metadata import read_audio_metadata
from .._utils.trim_audio import trim_audio


async def build_analysis_enabled(
    file_info_spec: FileInfoSpec,
    file_blob: FileBlob,
    *,
    run_context: RunContext,
    settings: AudioFileInfoBuilderSettings,
) -> BuildResult:
    duration = (await read_audio_metadata(file_blob.file_path)).duration

    output_base_path = create_local_repository(run_context).generate_cache_path(
        os.path.join("intermediate", "audio", file_blob.hash_string)
    )

    # segmentation
    segment_audio_file_blob: FileBlob | None = None

    if not _has_audio_segment(file_info_spec, duration=duration):
        segment_audio_file_blob = file_blob

    else:
        segment_file_path = _get_trimmed_file_path(
            output_base_path,
            file_info_spec=file_info_spec,
            input_file_path=file_blob.file_path,
        )

        if not os.path.exists(segment_file_path):
            await trim_audio(
                file_blob.file_path,
                segment_file_path,
                start_time=file_info_spec.get("start_time", 0.0),
                end_time=file_info_spec.get("end_time", -1.0),
            )

        segment_audio_file_blob = await kfa.read_file(segment_file_path)

        if not segment_audio_file_blob:
            raise FileNotFoundError(segment_file_path)

    # encoding
    encoded_file_path = _get_encoded_file_path(
        output_base_path,
        file_info_spec=file_info_spec,
    )

    if not os.path.exists(encoded_file_path):
        await encode_mono_16kbps_mp3(
            segment_audio_file_blob.file_path,
            encoded_file_path,
        )

    encoded_audio_file_blob = await kfa.read_file(encoded_file_path)

    if not encoded_audio_file_blob:
        raise FileNotFoundError(encoded_file_path)

    # analysis
    bundle_file_path = _get_bundle_file_path(
        output_base_path,
        file_info_spec=file_info_spec,
        settings=settings,
    )

    bundle_file_blob = await kfa.read_file(bundle_file_path)

    if not bundle_file_blob:
        # consume audio source through all configured consumers
        audio_events: list[AudioEvent] = []

        consumers = [
            audio_consumer_registry.resolve(specifier, run_context=run_context)
            for specifier in settings.audio_consumers
        ]

        if consumers:
            audio_source = audio_source_registry.resolve(settings.audio_source)

            async with audio_source.open(segment_audio_file_blob.file_path):
                async for chunk in audio_source.read():
                    for consumer in consumers:
                        audio_events.extend(await consumer.accept(chunk))

            for consumer in consumers:
                audio_events.extend(await consumer.flush())

        # build per-bundler FileBundles, then merge with the encoded-audio bundle
        audio_bundle = _build_audio_media_bundle(encoded_audio_file_blob)

        bundler_bundles: list[FileBundle] = []

        for specifier in settings.audio_event_bundlers:
            bundler = audio_event_bundler_registry.resolve(specifier)
            sub_bundle = bundler.bundle(audio_events)

            if sub_bundle is not None:
                bundler_bundles.append(sub_bundle)

        bundle = reduce(lambda a, b: a + b, bundler_bundles, audio_bundle)
        bundle_raw_data = bundle.to_bytes()

        await kfa.write_binary(bundle_file_path, bundle_raw_data)

        bundle_file_blob = FileBlob(
            bundle_file_path,
            mime_type=FileBundle.MIME_TYPE,
            raw_data=bundle_raw_data,
        )

    file_size = len(bundle_file_blob.raw_data)

    token_count = calc_audio_token(
        (await read_audio_metadata(segment_audio_file_blob.file_path)).duration
    )

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
                "intermediate_file_path": bundle_file_blob.file_path,
                "asset_uri": None,
            }
        ),
        file_blob=file_blob,
        intermediate_file_blob=bundle_file_blob,
    )


def _has_audio_segment(file_info_spec: FileInfoSpec, *, duration: float) -> bool:
    start_time = normalize_time(file_info_spec.get("start_time", 0.0), duration)
    end_time = normalize_time(file_info_spec.get("end_time", -1.0), duration)

    return start_time != 0.0 or end_time != duration


def _get_trimmed_file_path(
    output_base_path: str,
    *,
    file_info_spec: FileInfoSpec,
    input_file_path: str,
) -> str:
    start_time = file_info_spec.get("start_time", 0.0)
    end_time = file_info_spec.get("end_time", -1.0)
    extension = os.path.splitext(input_file_path)[1] or ".audio"
    return f"{output_base_path}_trimmed_{start_time:.1f}_{end_time:.1f}{extension}"


def _get_encoded_file_path(
    output_base_path: str,
    *,
    file_info_spec: FileInfoSpec,
) -> str:
    start_time = file_info_spec.get("start_time", 0.0)
    end_time = file_info_spec.get("end_time", -1.0)
    return f"{output_base_path}_encoded_{start_time:.1f}_{end_time:.1f}.mp3"


def _get_bundle_file_path(
    output_base_path: str,
    *,
    file_info_spec: FileInfoSpec,
    settings: AudioFileInfoBuilderSettings,
) -> str:
    signature_source = {
        "bundle_version": 9,
        "start_time": file_info_spec.get("start_time", 0.0),
        "end_time": file_info_spec.get("end_time", -1.0),
        "settings": settings.model_dump(mode="json"),
    }

    signature = sha1(
        repr(sorted(signature_source.items())).encode("utf-8")
    ).hexdigest()[:12]

    return f"{output_base_path}_analysis_{signature}.zip"


def _build_audio_media_bundle(audio_file_blob: FileBlob) -> FileBundle:
    audio_file_path = "audio.mp3"

    return FileBundle.create(
        manifest_contents=[
            FileBundleMediaContent(
                type="audio",
                file_path=audio_file_path,
                mime_type=audio_file_blob.mime_type,
                visibility="supported",
            ),
        ],
        files={audio_file_path: audio_file_blob.raw_data},
    )
