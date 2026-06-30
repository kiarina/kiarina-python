from pathlib import Path

import pytest


@pytest.fixture
def assets_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent / "tests" / "assets"


@pytest.fixture
def key_prefix(request):
    return f"pytest:{request.module.__name__}:{request.node.name}:"


@pytest.fixture
def index_name(request):
    return f"pytest_{request.module.__name__}_{request.node.name}"


@pytest.fixture
def fields():
    return [{"type": "text", "name": "title"}]


@pytest.fixture
def redis():
    raise NotImplementedError("Override this fixture in conftest.py")
