from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import BaseCostRecorder
from kiarina.agi.run_context import RunContext


class MyCostRecorder(BaseCostRecorder): ...


async def test_base_cost_recorder(run_context: RunContext) -> None:
    cost_recorder = MyCostRecorder()

    cost_record = CostRecord(
        microdollars=1000,
        kind="chat",
        source="test",
        metadata={"detail": "test"},
    )

    cost_recorder.add(cost_record)
    assert len(cost_recorder.records) == 1
    assert cost_recorder.total_microdollars == 1000
    assert cost_recorder.total_dollars == 0.001

    await cost_recorder.flush(run_context)
    assert len(cost_recorder.records) == 0
