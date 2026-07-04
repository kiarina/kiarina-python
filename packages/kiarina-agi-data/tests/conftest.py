import re
from collections.abc import Iterator
from typing import TypedDict

import pytest

from kiarina.agi.file_info import (
    AudioFileInfo,
    ImageFileInfo,
    OtherFileInfo,
    PDFFileInfo,
    TextFileInfo,
    VideoFileInfo,
)
from kiarina.agi.run_context import RunContext, settings_manager
from kiarina.utils.app import configure, reset


class FileInfoArgs(TypedDict):
    uri_or_file_path: str
    mime_type: str
    file_hash: str
    file_size: int
    token_count: int
    intermediate_file_path: str | None
    asset_uri: str | None


def create_file_info_args(
    *,
    uri_or_file_path: str = "/tmp/sample",
    mime_type: str = "application/octet-stream",
) -> FileInfoArgs:
    return {
        "uri_or_file_path": uri_or_file_path,
        "mime_type": mime_type,
        "file_hash": "dummy-hash",
        "file_size": 100,
        "token_count": 100,
        "intermediate_file_path": None,
        "asset_uri": None,
    }


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Iterator[None]:
    configure(app_author="kiarina", app_name="kiarina-agi-data")
    cli_args = settings_manager.cli_args
    settings_manager.cli_args = {"node_id": "pytest"}
    yield
    settings_manager.cli_args = cli_args
    reset()


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture
def text_file_info() -> TextFileInfo:
    raw_text = "\n".join(f"Line {index}" for index in range(1, 101))
    return TextFileInfo(
        **create_file_info_args(
            uri_or_file_path="/tmp/sample.txt",
            mime_type="text/plain",
        ),
        line_count=100,
        raw_text=raw_text,
    )


@pytest.fixture
def image_file_info() -> ImageFileInfo:
    return ImageFileInfo(
        **create_file_info_args(
            uri_or_file_path="/tmp/sample.png",
            mime_type="image/png",
        ),
        width=640,
        height=480,
    )


@pytest.fixture
def audio_file_info() -> AudioFileInfo:
    return AudioFileInfo(
        **create_file_info_args(
            uri_or_file_path="/tmp/sample.mp3",
            mime_type="audio/mpeg",
        ),
        duration=10.0,
    )


@pytest.fixture
def video_file_info() -> VideoFileInfo:
    return VideoFileInfo(
        **create_file_info_args(
            uri_or_file_path="/tmp/sample.mp4",
            mime_type="video/mp4",
        ),
        width=640,
        height=480,
        duration=10.0,
    )


@pytest.fixture
def pdf_file_info() -> PDFFileInfo:
    return PDFFileInfo(
        **create_file_info_args(
            uri_or_file_path="/tmp/sample.pdf",
            mime_type="application/pdf",
        ),
        page_count=10,
    )


@pytest.fixture
def other_file_info() -> OtherFileInfo:
    return OtherFileInfo(**create_file_info_args(uri_or_file_path="/tmp/sample.bin"))
