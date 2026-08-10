from pathlib import Path

from PIL import Image

from kiarina.agi.file_bundle import FileBundleMediaContent
from kiarina.agi.file_info_builder_impl.video._operations.build_frame_bundle import (
    build_frame_bundle,
)


async def test_build_frame_bundle(short_video_file_path: Path) -> None:
    bundle = await build_frame_bundle(
        str(short_video_file_path),
        analysis_fps=1.0,
    )

    assert len(bundle.manifest.contents) == 13

    first = bundle.manifest.contents[0]
    last = bundle.manifest.contents[-1]
    assert isinstance(first, FileBundleMediaContent)
    assert isinstance(last, FileBundleMediaContent)
    assert first.type == "image"
    assert first.visibility == "unsupported"
    assert first.prefix_text == '<image timestamp="0.000" />'
    assert last.prefix_text == '<image timestamp="12.000" />'

    image_path = first.file_path
    image = Image.open(__import__("io").BytesIO(bundle.files[image_path]))
    assert image.format == "JPEG"
    assert image.size == (1600, 900)
