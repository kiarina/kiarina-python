import re
from collections.abc import Iterator
from pathlib import Path
from typing import TypedDict

import pytest
from pydantic import BaseModel, Field

from kiarina.agi.chat_model import ChatModel, chat_model_registry
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.file_info import (
    AudioFileInfo,
    FileInfo,
    ImageFileInfo,
    OtherFileInfo,
    PDFFileInfo,
    TextFileInfo,
    VideoFileInfo,
)
from kiarina.agi.history import History
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolCall,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo, create_tool_info
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
    uri_or_file_path: str,
    mime_type: str = "application/octet-stream",
) -> FileInfoArgs:
    return {
        "uri_or_file_path": uri_or_file_path,
        "mime_type": mime_type,
        "file_hash": "dummy-hash",
        "file_size": Path(uri_or_file_path).stat().st_size,
        "token_count": 100,
        "intermediate_file_path": None,
        "asset_uri": None,
    }


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Iterator[None]:
    configure(app_author="kiarina", app_name="kiarina-agi-flow")
    yield
    reset()


# --------------------------------------------------
# Logger
# --------------------------------------------------


# @pytest.fixture(autouse=True)
# def setup_request_logger():
#     from kiarina.agi.request_logger import settings_manager
#
#     settings_manager.cli_args = {"default": "console"}
#     yield
#     settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
def setup_chat_logger() -> Iterator[None]:
    from kiarina.agi.chat_logger import settings_manager

    settings_manager.cli_args = {"default": "console"}
    yield
    settings_manager.cli_args = {}


# --------------------------------------------------
# Cost Recorder
# --------------------------------------------------


@pytest.fixture
def cost_recorder() -> CostRecorder:
    from kiarina.agi.cost_recorder_impl.null import NullCostRecorder

    return NullCostRecorder()


# --------------------------------------------------
# Chat Models
# --------------------------------------------------


@pytest.fixture(autouse=True)
def setup_chat_model() -> Iterator[None]:
    from kiarina.agi.chat_model import settings_manager

    settings_manager.cli_args = {"default": "mock"}
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def chat_model() -> ChatModel:
    chat_model = chat_model_registry.resolve("mock")
    chat_model.config.provider_config.update(
        {
            "input_enabled": {
                "image": True,
                "audio": False,
                "video": False,
                "pdf": True,
            },
        }
    )
    return chat_model


@pytest.fixture
def all_enabled_chat_model() -> ChatModel:
    chat_model = chat_model_registry.resolve("mock")
    chat_model.config.provider_config.update(
        {
            "input_enabled": {
                "image": True,
                "audio": True,
                "video": True,
                "pdf": True,
            },
        }
    )
    return chat_model


# --------------------------------------------------
# File Paths
# --------------------------------------------------


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parents[3] / "tests" / "assets"


@pytest.fixture
def text_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "txt" / "hello_world_11b.txt")


@pytest.fixture
def image_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "png" / "miineko_256x256_799b.png")


@pytest.fixture
def audio_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "mp3" / "tone_2s_16kb.mp3")


@pytest.fixture
def video_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "mp4" / "shape_animation_1600x900_24fps_13s_4400kb.mp4")


@pytest.fixture
def pdf_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "pdf" / "text_only_portrait_1p_17kb.pdf")


@pytest.fixture
def other_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "csv" / "monthly_temperature_13row_141b.csv")


# --------------------------------------------------
# File Infos
# --------------------------------------------------


@pytest.fixture
def text_file_info(text_file_path: str) -> FileInfo:
    raw_text = Path(text_file_path).read_text()
    return TextFileInfo(
        **create_file_info_args(
            uri_or_file_path=text_file_path,
            mime_type="text/plain",
        ),
        line_count=len(raw_text.splitlines()),
        raw_text=raw_text,
    )


@pytest.fixture
def image_file_info(image_file_path: str) -> FileInfo:
    return ImageFileInfo(
        **create_file_info_args(
            uri_or_file_path=image_file_path,
            mime_type="image/png",
        ),
        width=256,
        height=256,
    )


@pytest.fixture
def audio_file_info(audio_file_path: str) -> FileInfo:
    return AudioFileInfo(
        **create_file_info_args(
            uri_or_file_path=audio_file_path,
            mime_type="audio/mpeg",
        ),
        duration=2.0,
    )


@pytest.fixture
def video_file_info(video_file_path: str) -> FileInfo:
    return VideoFileInfo(
        **create_file_info_args(
            uri_or_file_path=video_file_path,
            mime_type="video/mp4",
        ),
        width=1600,
        height=900,
        duration=13.0,
    )


@pytest.fixture
def pdf_file_info(pdf_file_path: str) -> FileInfo:
    return PDFFileInfo(
        **create_file_info_args(
            uri_or_file_path=pdf_file_path,
            mime_type="application/pdf",
        ),
        page_count=1,
    )


@pytest.fixture
def other_file_info(other_file_path: str) -> FileInfo:
    return OtherFileInfo(
        **create_file_info_args(
            uri_or_file_path=other_file_path,
            mime_type="text/csv",
        )
    )


# --------------------------------------------------
# Tool Infos
# --------------------------------------------------


@pytest.fixture
def tool_info() -> ToolInfo:
    class get_weather(BaseModel):
        """Get the weather for a given location."""

        reason: str = Field(description="Reason for getting the weather")

    return create_tool_info(get_weather)


@pytest.fixture
def tool_infos() -> list[ToolInfo]:
    class get_weather(BaseModel):
        """Get the weather for a given location."""

        reason: str = Field(description="Reason for getting the weather")

    class get_news(BaseModel):
        """Get the latest news for a given topic."""

        reason: str = Field(description="Reason for getting the news")

    return [
        create_tool_info(get_weather),
        create_tool_info(get_news),
    ]


# --------------------------------------------------
# Messages
# --------------------------------------------------


@pytest.fixture
def messages(image_file_info: FileInfo) -> list[Message]:
    return [
        HumanMessage.create("Hello"),
        AIMessage.create("Hello"),
        HumanMessage.create("Create a image of a cat"),
        AIMessage.create(
            tool_calls=[
                ToolCall(
                    name="generate_image",
                    args={"instructions": "Create a image of a cat"},
                    id="123",
                )
            ]
        ),
        ToolMessage.create(
            "image generated",
            [image_file_info],
            tool_name="generate_image",
            tool_call_args={"instructions": "Create a image of a cat"},
            tool_call_id="123",
        ),
    ]


# --------------------------------------------------
# History
# --------------------------------------------------


@pytest.fixture
def history(messages: list[Message]) -> History:
    history = History()

    for message in messages:
        history.add_message(message)

    return history
