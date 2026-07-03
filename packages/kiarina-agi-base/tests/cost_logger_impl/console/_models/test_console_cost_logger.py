import pytest

from kiarina.agi.base.cost_logger import settings_manager
from kiarina.agi.base.cost_logger_impl.console import ConsoleCostLogger
from kiarina.agi.base.cost_record import CostRecord


@pytest.fixture(autouse=True)
def setup():
    settings_manager.cli_args = {
        "currency": "JPY",
        "exchange_rate": 150.0,
        "decimal_places": 2,
    }
    yield
    settings_manager.cli_args = {}


def test_cost_add():
    logger = ConsoleCostLogger()

    cost_record = CostRecord(
        kind="test",
        microdollars=123456,
        source="test_source",
        metadata={"model": "mock"},
    )

    logger.log_cost_add(cost_record)


def test_cost_flush():
    logger = ConsoleCostLogger()

    cost_records = [
        CostRecord(
            kind="test",
            microdollars=123456,
            source="test_source_1",
            metadata={"model": "mock"},
        ),
        CostRecord(
            kind="test",
            microdollars=654321,
            source="test_source_2",
            metadata={"model": "mock"},
        ),
    ]

    logger.log_cost_flush(cost_records)
