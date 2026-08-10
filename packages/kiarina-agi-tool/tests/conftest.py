import re
from collections.abc import Iterator
from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.file_info import FileInfo, ImageFileInfo, TextFileInfo
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_text_token
from kiarina.utils.app import configure, reset


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
    configure(app_author="kiarina", app_name="kiarina-agi-tool")
    yield
    reset()


@pytest.fixture
def cost_recorder() -> CostRecorder:
    from kiarina.agi.cost_recorder_impl.null import NullCostRecorder

    return NullCostRecorder()


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
def text_file_info(text_file_path: str) -> FileInfo:
    file_path = Path(text_file_path)
    raw_text = file_path.read_text()
    return TextFileInfo(
        uri_or_file_path=text_file_path,
        mime_type="text/plain",
        file_hash="dummy-hash",
        file_size=file_path.stat().st_size,
        token_count=calc_text_token(raw_text),
        intermediate_file_path=None,
        asset_uri=None,
        line_count=len(raw_text.splitlines()),
        raw_text=raw_text,
    )


@pytest.fixture
def image_file_info(image_file_path: str) -> FileInfo:
    file_path = Path(image_file_path)
    return ImageFileInfo(
        uri_or_file_path=image_file_path,
        mime_type="image/png",
        file_hash="dummy-hash",
        file_size=file_path.stat().st_size,
        token_count=100,
        intermediate_file_path=None,
        asset_uri=None,
        width=256,
        height=256,
    )
