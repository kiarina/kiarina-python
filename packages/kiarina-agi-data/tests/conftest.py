import re
from collections.abc import Callable

import pytest

from kiarina.agi.base.run_context import RunContext, settings_manager
from kiarina.agi.data.file_info import (
    AudioFileInfo,
    ImageFileInfo,
    OtherFileInfo,
    PDFFileInfo,
    TextFileInfo,
    VideoFileInfo,
)
from kiarina.utils.app import configure, reset


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> None:
    configure(app_author="kiarina", app_name="kiarina-agi-data")
    cli_args = settings_manager.cli_args
    settings_manager.cli_args = {"node_id": "pytest"}
    yield
    settings_manager.cli_args = cli_args
    reset()


@pytest.fixture
def run_context(request) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi.data",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture
def file_info_factory() -> Callable[..., dict[str, object]]:
    def factory(**overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "uri_or_file_path": "/tmp/sample",
            "mime_type": "application/octet-stream",
            "file_hash": "dummy-hash",
            "file_size": 100,
            "token_count": 100,
            "intermediate_file_path": None,
            "asset_uri": None,
        }
        values.update(overrides)
        return values

    return factory


@pytest.fixture
def text_file_info(
    file_info_factory: Callable[..., dict[str, object]],
) -> TextFileInfo:
    raw_text = "\n".join(f"Line {index}" for index in range(1, 101))
    return TextFileInfo(
        **file_info_factory(
            uri_or_file_path="/tmp/sample.txt",
            mime_type="text/plain",
        ),
        line_count=100,
        raw_text=raw_text,
    )


@pytest.fixture
def image_file_info(
    file_info_factory: Callable[..., dict[str, object]],
) -> ImageFileInfo:
    return ImageFileInfo(
        **file_info_factory(
            uri_or_file_path="/tmp/sample.png",
            mime_type="image/png",
        ),
        width=640,
        height=480,
    )


@pytest.fixture
def audio_file_info(
    file_info_factory: Callable[..., dict[str, object]],
) -> AudioFileInfo:
    return AudioFileInfo(
        **file_info_factory(
            uri_or_file_path="/tmp/sample.mp3",
            mime_type="audio/mpeg",
        ),
        duration=10.0,
    )


@pytest.fixture
def video_file_info(
    file_info_factory: Callable[..., dict[str, object]],
) -> VideoFileInfo:
    return VideoFileInfo(
        **file_info_factory(
            uri_or_file_path="/tmp/sample.mp4",
            mime_type="video/mp4",
        ),
        width=640,
        height=480,
        duration=10.0,
    )


@pytest.fixture
def pdf_file_info(
    file_info_factory: Callable[..., dict[str, object]],
) -> PDFFileInfo:
    return PDFFileInfo(
        **file_info_factory(
            uri_or_file_path="/tmp/sample.pdf",
            mime_type="application/pdf",
        ),
        page_count=10,
    )


@pytest.fixture
def other_file_info(
    file_info_factory: Callable[..., dict[str, object]],
) -> OtherFileInfo:
    return OtherFileInfo(**file_info_factory(uri_or_file_path="/tmp/sample.bin"))
