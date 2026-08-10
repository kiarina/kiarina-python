from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleContentInput,
    FileBundleMediaContent,
)
from kiarina.agi.video_source_impl.file import (
    FileVideoSource,
    FileVideoSourceSettings,
)

from .._utils.encode_video_frame_jpeg import encode_video_frame_jpeg


async def build_frame_bundle(
    video_file_path: str,
    *,
    analysis_fps: float,
) -> FileBundle:
    video_source = FileVideoSource(
        FileVideoSourceSettings(fps=analysis_fps, start_timestamp=0.0)
    )
    contents: list[FileBundleContentInput] = []
    files: dict[str, bytes] = {}

    async with video_source.open(video_file_path):
        async for frame in video_source.read():
            file_path = f"frames/{frame.frame_index:06d}.jpg"
            contents.append(
                FileBundleMediaContent(
                    type="image",
                    file_path=file_path,
                    mime_type="image/jpeg",
                    visibility="unsupported",
                    prefix_text=f'<image timestamp="{frame.timestamp:.3f}" />',
                )
            )
            files[file_path] = encode_video_frame_jpeg(frame.pixels)

    return FileBundle.create(manifest_contents=contents, files=files)
