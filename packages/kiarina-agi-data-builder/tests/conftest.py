import re
from collections.abc import Iterator
from pathlib import Path

import pytest

from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure, reset


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Iterator[None]:
    configure(app_author="kiarina", app_name="kiarina-agi-data-builder")
    yield
    reset()


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parents[3] / "tests" / "assets"


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


# --------------------------------------------------
# File Paths
# --------------------------------------------------


@pytest.fixture
def text_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "txt" / "hello_world_11b.txt")


@pytest.fixture
def large_image_file_path(test_data_dir: Path) -> str:
    return str(test_data_dir / "jpg" / "grid_4000x3000_1400kb.jpg")


@pytest.fixture
def video_file_path(test_data_dir: Path) -> Path:
    return test_data_dir / "mp4" / "shape_animation_1600x900_24fps_13s_4400kb.mp4"


@pytest.fixture
def short_video_file_path(test_data_dir: Path) -> Path:
    return test_data_dir / "mp4" / "shape_animation_1600x900_24fps_13s_4400kb.mp4"


@pytest.fixture
def pdf_file_path(test_data_dir: Path) -> Path:
    return test_data_dir / "pdf" / "text_only_portrait_1p_17kb.pdf"


@pytest.fixture
def pdf_with_images_file_path(test_data_dir: Path) -> Path:
    return test_data_dir / "pdf" / "image_and_text_3p_1800kb.pdf"


@pytest.fixture
def many_page_pdf_file_path(test_data_dir: Path) -> Path:
    return test_data_dir / "pdf" / "image_and_text_3p_1800kb.pdf"
