from pathlib import Path

import pytest

from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import (
    AudioFileInfo,
    FileInfo,
    ImageFileInfo,
    PDFFileInfo,
    TextFileInfo,
    VideoFileInfo,
)
from kiarina.agi.file_info_adjuster import trim_file_by_token
from kiarina.agi.file_info_adjuster._utils.trim_file_by_token import (
    _trim_media_file_by_token,
    _trim_pdf_file_by_token,
    _trim_text_file_by_token,
)
from kiarina.agi.file_info_builder import build_file_info
from kiarina.agi.run_context import RunContext


@pytest.mark.parametrize(
    "file_path, keep_token_count, file_info_type, is_none",
    [
        pytest.param(
            "json/user_list_5row_1kb.json", 50, TextFileInfo, False, id="text"
        ),
        pytest.param(
            "png/miineko_256x256_799b.png", 50, ImageFileInfo, True, id="image"
        ),
        pytest.param("mp3/tone_2s_16kb.mp3", 3000, AudioFileInfo, False, id="audio"),
        pytest.param(
            "mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4",
            3000,
            VideoFileInfo,
            False,
            id="video",
        ),
        pytest.param(
            "pdf/image_and_text_3p_1800kb.pdf", 3000, PDFFileInfo, False, id="pdf"
        ),
        pytest.param("html/simple_160b.html", 50, TextFileInfo, False, id="html"),
    ],
)
async def test_trim_file_by_token(
    file_path: str,
    keep_token_count: int,
    file_info_type: type[FileInfo],
    is_none: bool,
    run_context: RunContext,
    test_data_dir: Path,
) -> None:
    file_blob = await get_file_blob(
        str(test_data_dir / file_path), run_context=run_context
    )
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": str(test_data_dir / file_path)},
        file_blob,
        run_context=run_context,
    )
    assert isinstance(file.file_info, file_info_type)

    new_file_info = await trim_file_by_token(
        file_info=file.file_info,
        file_blob=file_blob,
        keep_token_count=keep_token_count,
        run_context=run_context,
    )

    if is_none:
        assert new_file_info is None
    else:
        assert new_file_info is not None
        assert new_file_info.token_count <= keep_token_count


@pytest.mark.parametrize(
    "keep_token_count, is_none",
    [
        (0, True),
        (1, True),
        (50, False),
    ],
)
async def test_trim_text_file_by_token(
    keep_token_count: int, is_none: bool, run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await get_file_blob(
        str(test_data_dir / "json/user_list_5row_1kb.json"), run_context=run_context
    )
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": str(test_data_dir / "json/user_list_5row_1kb.json")},
        file_blob,
        run_context=run_context,
    )
    assert isinstance(file.file_info, TextFileInfo)

    new_file_info = await _trim_text_file_by_token(
        file_info=file.file_info,
        file_blob=file_blob,
        keep_token_count=keep_token_count,
        run_context=run_context,
    )

    if is_none:
        assert new_file_info is None
    else:
        assert new_file_info is not None
        assert new_file_info.token_count <= keep_token_count
        print(new_file_info.raw_text)


@pytest.mark.parametrize(
    "keep_token_count, is_none",
    [
        (0, True),
        (1, True),
        (3000, False),
    ],
)
async def test_trim_media_file_by_token(
    keep_token_count: int, is_none: bool, run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await get_file_blob(
        str(test_data_dir / "mp3/tone_2s_16kb.mp3"), run_context=run_context
    )
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": str(test_data_dir / "mp3/tone_2s_16kb.mp3")},
        file_blob,
        run_context=run_context,
    )
    assert isinstance(file.file_info, AudioFileInfo)

    new_file_info = await _trim_media_file_by_token(
        file_info=file.file_info,
        file_blob=file_blob,
        keep_token_count=keep_token_count,
        run_context=run_context,
    )

    if is_none:
        assert new_file_info is None
    else:
        assert new_file_info is not None
        assert new_file_info.token_count <= keep_token_count


@pytest.mark.parametrize(
    "keep_token_count, is_none",
    [
        (0, True),
        (1, True),
        (3000, False),
    ],
)
async def test_trim_pdf_file_by_token(
    keep_token_count: int, is_none: bool, run_context: RunContext, test_data_dir: Path
) -> None:
    file_blob = await get_file_blob(
        str(test_data_dir / "pdf/image_and_text_3p_1800kb.pdf"), run_context=run_context
    )
    assert file_blob is not None

    file = await build_file_info(
        {"uri_or_file_path": str(test_data_dir / "pdf/image_and_text_3p_1800kb.pdf")},
        file_blob,
        run_context=run_context,
    )
    assert isinstance(file.file_info, PDFFileInfo)

    new_file_info = await _trim_pdf_file_by_token(
        file_info=file.file_info,
        file_blob=file_blob,
        keep_token_count=keep_token_count,
        run_context=run_context,
    )

    if is_none:
        assert new_file_info is None
    else:
        assert new_file_info is not None
        assert new_file_info.token_count <= keep_token_count
