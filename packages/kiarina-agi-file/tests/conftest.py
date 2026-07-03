import re
from collections.abc import Iterator
from typing import Any

import pytest

from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure, reset


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> Iterator[None]:
    configure(app_author="kiarina", app_name="kiarina-agi-file")
    yield
    reset()


@pytest.fixture
def run_context(request: Any) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi.file",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )
