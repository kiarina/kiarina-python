from collections.abc import Iterator

import pytest

from kiarina.agi.state import StateContext
from kiarina.agi.state_machine import StateMachine
from kiarina.agi.workflow import workflow, workflow_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    workflow_registry.clear()


def test_workflow_registry() -> None:

    @workflow
    def ExampleWorkflow(ctx: StateContext) -> StateMachine:
        return StateMachine(ctx)

    workflow_registry.register("test", ExampleWorkflow)

    instance = workflow_registry.create("test")
    assert isinstance(instance, ExampleWorkflow)
    assert instance.name == "test"
