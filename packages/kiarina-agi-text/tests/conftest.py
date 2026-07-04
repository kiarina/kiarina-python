import os
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, Field

from kiarina.agi.chat_model import ChatModel, chat_model_registry
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import (
    AudioFileInfo,
    ImageFileInfo,
    OtherFileInfo,
    PDFFileInfo,
    TextFileInfo,
    VideoFileInfo,
)
from kiarina.agi.langchain_chat_provider import (
    LangChainMediaConverter,
    LCMessage,
    LCToolInfo,
)
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolCall,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import create_tool_info
from kiarina.utils.app import configure, reset
from kiarina.utils.file import FileBlob, read_file
from kiarina.utils.mime import MIMEBlob


def _get_chat_model_name() -> str:
    return os.getenv("KIARINA_AGI_TEXT_TEST_CHAT_MODEL", "mock").strip() or "mock"


def pytest_report_header() -> str:
    return f"chat model: {_get_chat_model_name()}"


@pytest.fixture(scope="session")
def chat_model_name() -> str:
    return _get_chat_model_name()


@pytest.fixture(autouse=True)
def skip_costly(request: pytest.FixtureRequest) -> None:
    costly_enabled = os.getenv("KIARINA_TEST_COSTLY", "0") == "1"
    if request.node.get_closest_marker("costly") and not costly_enabled:
        pytest.skip("Set KIARINA_TEST_COSTLY=1 to run this test.")


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Iterator[None]:
    configure(app_author="kiarina", app_name="kiarina-agi-text")
    yield
    reset()


@pytest.fixture(autouse=True)
def setup_chat_logger() -> Any:
    from kiarina.agi.chat_logger import settings_manager

    settings_manager.cli_args = {"default": "console"}
    yield
    settings_manager.cli_args = {}


# --------------------------------------------------
# Common Fixtures
# --------------------------------------------------


@pytest.fixture
def run_context(request: Any) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture
async def cost_recorder(run_context: Any) -> Any:
    from kiarina.agi.cost_recorder_impl.null import NullCostRecorder

    recorder = NullCostRecorder()
    yield recorder
    await recorder.flush(run_context)


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
def large_text_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "txt" / "utf-8_1027line_125kb.txt")


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
# File Blobs
# --------------------------------------------------


@pytest.fixture
def text_file_blob(text_file_path: Any) -> FileBlob:
    file_blob = read_file(text_file_path)
    assert file_blob is not None
    return file_blob


@pytest.fixture
def large_text_file_blob(large_text_file_path: Any) -> FileBlob:
    file_blob = read_file(large_text_file_path)
    assert file_blob is not None
    return file_blob


@pytest.fixture
def image_file_blob(image_file_path: str) -> FileBlob:
    file_blob = read_file(image_file_path)
    assert file_blob is not None
    return file_blob


@pytest.fixture
def audio_file_blob(audio_file_path: str) -> FileBlob:
    file_blob = read_file(audio_file_path)
    assert file_blob is not None
    return file_blob


@pytest.fixture
def video_file_blob(video_file_path: str) -> FileBlob:
    file_blob = read_file(video_file_path)
    assert file_blob is not None
    return file_blob


@pytest.fixture
def pdf_file_blob(pdf_file_path: str) -> FileBlob:
    file_blob = read_file(pdf_file_path)
    assert file_blob is not None
    return file_blob


# --------------------------------------------------
# Tool Infos
# --------------------------------------------------


@pytest.fixture
def tool_info() -> Any:
    class get_weather(BaseModel):
        """Get the weather for a given location."""

        reason: str = Field(description="Reason for getting the weather")

    return create_tool_info(get_weather)


@pytest.fixture
def tool_infos() -> Any:
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


@pytest.fixture
def generate_tool_infos() -> Any:
    class generate_image(BaseModel):
        """Generate an image based on the given instructions."""

        instructions: str = Field(description="Instructions for generating the image")

    class generate_audio(BaseModel):
        """Generate an audio based on the given instructions."""

        instructions: str = Field(description="Instructions for generating the audio")

    class generate_video(BaseModel):
        """Generate a video based on the given instructions."""

        instructions: str = Field(description="Instructions for generating the video")

    class generate_pdf(BaseModel):
        """Generate a PDF based on the given instructions."""

        instructions: str = Field(description="Instructions for generating the PDF")

    return [
        create_tool_info(generate_image),
        create_tool_info(generate_audio),
        create_tool_info(generate_video),
        create_tool_info(generate_pdf),
    ]


@pytest.fixture
def large_tool_infos(
    tool_info: Any, generate_tool_infos: Any, large_text_file_blob: Any
) -> Any:
    large_tool_info = tool_info.copy()
    large_tool_info["description"] += "\n\n" + large_text_file_blob.raw_text
    return [*generate_tool_infos, large_tool_info]


# --------------------------------------------------
# File Infos
# --------------------------------------------------


@pytest.fixture
def file_info_factory() -> Callable[..., dict[str, Any]]:
    def factory(**overrides: Any) -> dict[str, Any]:
        file_path = str(overrides["uri_or_file_path"])
        values: dict[str, Any] = {
            "node_id": "pytest",
            "mime_type": "application/octet-stream",
            "file_hash": "dummy-hash",
            "file_size": Path(file_path).stat().st_size,
            "token_count": 100,
            "intermediate_file_path": None,
            "asset_uri": None,
        }
        values.update(overrides)
        return values

    return factory


@pytest.fixture
def text_file_info(
    text_file_path: str,
    file_info_factory: Callable[..., dict[str, Any]],
) -> TextFileInfo:
    raw_text = Path(text_file_path).read_text()
    return TextFileInfo(
        **file_info_factory(uri_or_file_path=text_file_path, mime_type="text/plain"),
        line_count=len(raw_text.splitlines()),
        raw_text=raw_text,
    )


@pytest.fixture
def image_file_info(
    image_file_path: str,
    file_info_factory: Callable[..., dict[str, Any]],
) -> ImageFileInfo:
    return ImageFileInfo(
        **file_info_factory(uri_or_file_path=image_file_path, mime_type="image/png"),
        width=256,
        height=256,
    )


@pytest.fixture
def audio_file_info(
    audio_file_path: str,
    file_info_factory: Callable[..., dict[str, Any]],
) -> AudioFileInfo:
    return AudioFileInfo(
        **file_info_factory(uri_or_file_path=audio_file_path, mime_type="audio/mpeg"),
        duration=2.0,
    )


@pytest.fixture
def video_file_info(
    video_file_path: str,
    file_info_factory: Callable[..., dict[str, Any]],
) -> VideoFileInfo:
    return VideoFileInfo(
        **file_info_factory(uri_or_file_path=video_file_path, mime_type="video/mp4"),
        width=1600,
        height=900,
        duration=13.0,
    )


@pytest.fixture
def pdf_file_info(
    pdf_file_path: str,
    file_info_factory: Callable[..., dict[str, Any]],
) -> PDFFileInfo:
    return PDFFileInfo(
        **file_info_factory(
            uri_or_file_path=pdf_file_path,
            mime_type="application/pdf",
        ),
        page_count=1,
    )


@pytest.fixture
def other_file_info(
    other_file_path: str,
    file_info_factory: Callable[..., dict[str, Any]],
) -> OtherFileInfo:
    return OtherFileInfo(
        **file_info_factory(uri_or_file_path=other_file_path, mime_type="text/csv")
    )


# --------------------------------------------------
# Chat Capabilities
# --------------------------------------------------


@pytest.fixture
def capabilities() -> ChatCapabilities:
    return ChatCapabilities(
        input_enabled={
            "text": True,
            "image": True,
            "audio": False,
            "video": False,
            "pdf": True,
        },
    )


@pytest.fixture
def all_enabled_capabilities() -> ChatCapabilities:
    return ChatCapabilities(
        input_enabled={
            "text": True,
            "image": True,
            "audio": True,
            "video": True,
            "pdf": True,
        },
        output_enabled={
            "text": True,
            "image": True,
            "audio": True,
            "video": True,
            "pdf": True,
        },
    )


# --------------------------------------------------
# Media Converter
# --------------------------------------------------


@pytest.fixture
def media_converter() -> LangChainMediaConverter:
    class MyMediaConverter(LangChainMediaConverter):
        def to_image_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
            return {"type": "image", "mime_type": mime_blob.mime_type}

        def to_audio_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
            return {"type": "audio", "mime_type": mime_blob.mime_type}

        def to_video_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
            return {"type": "video", "mime_type": mime_blob.mime_type}

        def to_pdf_content(
            self, mime_blob: MIMEBlob, *, display_name: str
        ) -> dict[str, Any] | None:
            return {
                "type": "pdf",
                "mime_type": mime_blob.mime_type,
                "display_name": display_name,
            }

    return MyMediaConverter()


# --------------------------------------------------
# Chat Models
# --------------------------------------------------


@pytest.fixture
def chat_model(run_context: Any) -> ChatModel:
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
def all_enabled_chat_model(run_context: Any) -> ChatModel:
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
# Messages
# --------------------------------------------------


@pytest.fixture
def messages(image_file_info: Any) -> list[Message]:
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
        AIMessage.create("Created a cute image of a cat"),
    ]


# --------------------------------------------------
# LangChain Tool Infos
# --------------------------------------------------


@pytest.fixture
def lc_tool_infos(tool_infos: Any) -> list[LCToolInfo]:
    from kiarina.agi.langchain_chat_provider import from_tool_infos

    return from_tool_infos(tool_infos)


@pytest.fixture
def lc_generate_tool_infos(generate_tool_infos: Any) -> list[LCToolInfo]:
    from kiarina.agi.langchain_chat_provider import from_tool_infos

    return from_tool_infos(generate_tool_infos)


# --------------------------------------------------
# LangChain Messages
# --------------------------------------------------


@pytest.fixture
async def lc_messages(
    messages: Any, capabilities: Any, media_converter: Any, run_context: Any
) -> list[LCMessage]:
    from kiarina.agi.langchain_chat_provider import from_messages

    return await from_messages(
        messages,
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )
