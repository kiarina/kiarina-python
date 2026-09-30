from collections.abc import Iterator

import pytest
from pydantic import ValidationError

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
        "timezone": "Asia/Tokyo",
    }

    run_context = RunContext()

    assert run_context.organization_id == "org-123"
    assert run_context.user_id == "user-456"
    assert run_context.agent_id == "agent-789"
    assert run_context.timezone == "Asia/Tokyo"
    assert run_context.model_dump()["timezone"] == "Asia/Tokyo"

    assert str(run_context.zone_info) == "Asia/Tokyo"

    run_context = run_context.with_metadata(initial="value")
    assert run_context.metadata["initial"] == "value"


def test_allow_default_ids() -> None:
    settings_manager.cli_args = {}

    run_context = RunContext()

    assert run_context.organization_id == "default"
    assert run_context.user_id == "default"
    assert run_context.agent_id == "default"


def test_runner_id() -> None:
    assert RunContext().runner_id != RunContext().runner_id
    assert RunContext(runner_id="runner-1").runner_id == "runner-1"


def test_rejects_node_id() -> None:
    with pytest.raises(ValidationError, match="node_id"):
        RunContext.model_validate({"node_id": "node-001"})


def test_disallow_default_ids() -> None:
    settings_manager.cli_args = {"disallow_default_ids": True}

    with pytest.raises(ValueError, match=r"^organization_id must not be default$"):
        RunContext()


def test_rejects_old_time_zone_field() -> None:
    with pytest.raises(ValidationError, match="time_zone"):
        RunContext.model_validate({"time_zone": "Asia/Tokyo"})
