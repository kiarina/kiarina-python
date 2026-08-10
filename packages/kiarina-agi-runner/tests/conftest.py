import re
from collections.abc import Generator
from pathlib import Path

import pytest

from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.history import History
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolCall,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure, reset


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Generator[None, None, None]:
    configure(app_author="kiarina", app_name="kiarina-agi-runner")
    yield
    reset()


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture(autouse=True)
def setup() -> Generator[None, None, None]:
    from kiarina.agi.chat_model import settings_manager

    settings_manager.cli_args = {"default": "mock"}
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parents[3] / "tests" / "assets"


@pytest.fixture
def image_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "png" / "miineko_256x256_799b.png")


@pytest.fixture
async def image_file_info(image_file_path: str, run_context: RunContext) -> FileInfo:
    file_info = await load_file_info(image_file_path, run_context=run_context)
    assert file_info is not None
    return file_info


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


@pytest.fixture
def history(messages: list[Message]) -> History:
    history = History()

    for message in messages:
        history.add_message(message)

    return history
