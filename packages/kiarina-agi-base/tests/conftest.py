import re

import pytest

from kiarina.agi.base.run_context import RunContext
from kiarina.utils.app import configure, reset


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> None:
    configure(app_author="kiarina", app_name="kiarina-agi-base")
    yield
    reset()


@pytest.fixture
def run_context(request) -> RunContext:
    return RunContext(
        organization_id="kiarina.agi.base",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )
