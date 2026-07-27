from io import BytesIO
from pathlib import Path

from PIL import Image

from kiarina.agi.file_bundle import FileBundleMediaContent
from kiarina.agi.file_info_builder_impl.pdf._operations.build_page_image_bundle import (
    build_page_image_bundle,
)


async def test_build_page_image_bundle_renders_jpeg_pages(
    many_page_pdf_file_path: Path,
) -> None:
    bundle = await build_page_image_bundle(
        many_page_pdf_file_path.read_bytes(),
        analysis_dpi=144,
        start_page_number=5,
    )

    assert len(bundle.manifest.contents) == 3

    for index, content in enumerate(bundle.manifest.contents):
        assert isinstance(content, FileBundleMediaContent)
        assert content.type == "image"
        assert content.mime_type == "image/jpeg"
        assert content.visibility == "unsupported"
        assert content.prefix_text == (f'<image page_number="{5 + index}" />')
        assert content.file_path == f"pages/page_{5 + index:04d}.jpg"

    first = bundle.manifest.contents[0]
    assert isinstance(first, FileBundleMediaContent)

    with Image.open(BytesIO(bundle.files[first.file_path])) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert image.size == (1191, 1684)
