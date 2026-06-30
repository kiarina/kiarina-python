from pathlib import Path

import pytest


@pytest.fixture
def assets_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent / "tests" / "assets"
