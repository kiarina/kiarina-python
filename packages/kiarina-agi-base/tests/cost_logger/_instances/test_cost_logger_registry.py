from typing import Any

import pytest

from kiarina.agi.base.cost_logger import BaseCostLogger, cost_logger_registry


@pytest.fixture(autouse=True)
def cleanup() -> Any:
    yield
    cost_logger_registry.clear()


def test_cost_logger_registry() -> None:

    class ExampleCostLogger(BaseCostLogger):
        pass

    cost_logger_registry.register("test", ExampleCostLogger)

    cost_logger = cost_logger_registry.create("test")
    assert isinstance(cost_logger, ExampleCostLogger)
    assert cost_logger.name == "test"
