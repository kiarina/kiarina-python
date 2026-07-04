from collections.abc import Iterator

import pytest

from kiarina.agi.cost_recorder import BaseCostRecorder, cost_recorder_registry


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    cost_recorder_registry.clear()


def test_cost_recorder_registry() -> None:

    class ExampleCostRecorder(BaseCostRecorder):
        pass

    cost_recorder_registry.register("test", ExampleCostRecorder)

    cost_recorder = cost_recorder_registry.create("test")
    assert isinstance(cost_recorder, ExampleCostRecorder)
    assert cost_recorder.name == "test"
