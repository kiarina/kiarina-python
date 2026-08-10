from collections.abc import Iterator

import pytest

from kiarina.agi.run_context import RunContext, settings_manager


@pytest.fixture(autouse=True)
def cleanup_run_context() -> Iterator[None]:
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


def test_allow_default_ids() -> None:
    settings_manager.cli_args = {}

    run_context = RunContext()

    assert run_context.organization_id == "default"
    assert run_context.user_id == "default"
    assert run_context.agent_id == "default"
    assert run_context.node_id == "default"


def test_disallow_default_ids() -> None:
    settings_manager.cli_args = {"disallow_default_ids": True}

    with pytest.raises(ValueError, match=r"^organization_id must not be default$"):
        RunContext()
