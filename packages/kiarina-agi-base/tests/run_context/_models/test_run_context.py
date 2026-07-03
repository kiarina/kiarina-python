from typing import Any

import pytest

from kiarina.agi.base.run_context import RunContext, settings_manager


@pytest.fixture(autouse=True)
def cleanup_run_context() -> Any:
    cli_args = settings_manager.cli_args.copy()
    yield
    settings_manager.cli_args = cli_args


def test_run_context() -> None:
    settings_manager.cli_args = {
        "organization_id": "org-123",
        "user_id": "user-456",
        "agent_id": "agent-789",
        "node_id": "node-001",
    }

    run_context = RunContext()

    assert run_context.organization_id == "org-123"
    assert run_context.user_id == "user-456"
    assert run_context.agent_id == "agent-789"
    assert run_context.node_id == "node-001"

    print(f"zone_info: {run_context.zone_info}")

    run_context = run_context.with_metadata(initial="value")
    assert run_context.metadata["initial"] == "value"
