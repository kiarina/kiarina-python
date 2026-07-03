from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def assets_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent / "tests" / "assets"


@pytest.fixture
def key_prefix(request: Any) -> str:
    return f"pytest:{request.module.__name__}:{request.node.name}:"


@pytest.fixture
def index_name(request: Any) -> str:
    return f"pytest_{request.module.__name__}_{request.node.name}"


@pytest.fixture
def fields() -> Any:
    return [{"type": "text", "name": "title"}]


@pytest.fixture
def redis() -> None:
    raise NotImplementedError("Override this fixture in conftest.py")
