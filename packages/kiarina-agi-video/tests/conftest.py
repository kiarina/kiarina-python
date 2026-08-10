import os
import re
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure, reset


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Iterator[None]:
    configure(app_author="kiarina", app_name="kiarina-agi-video")
    yield
    reset()


@pytest.fixture(autouse=True)
def skip_costly(request: pytest.FixtureRequest) -> None:
    costly_enabled = os.getenv("KIARINA_TEST_COSTLY", "0") == "1"
    if request.node.get_closest_marker("costly") and not costly_enabled:
        pytest.skip("Set KIARINA_TEST_COSTLY=1 to run this test.")


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parents[3] / "tests" / "assets"


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi.video",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture
async def cost_recorder(run_context: RunContext) -> AsyncIterator[CostRecorder]:
    from kiarina.agi.cost_recorder_impl.null import NullCostRecorder

    recorder = NullCostRecorder()
    yield recorder
    await recorder.flush(run_context)


@pytest.fixture
def video_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "mp4" / "shape_animation_1600x900_24fps_13s_4400kb.mp4")


@pytest.fixture
def image_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "jpg" / "apple_1024x1024_138kb.jpg")
