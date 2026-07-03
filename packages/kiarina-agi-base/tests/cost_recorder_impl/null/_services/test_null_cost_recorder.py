from kiarina.agi.base.cost_record import CostRecord
from kiarina.agi.base.cost_recorder_impl.null import NullCostRecorder


async def test_null_cost_recorder(run_context) -> None:
    recorder = NullCostRecorder()

    recorder.add(
        CostRecord(
            microdollars=100,
            kind="chat",
            source="test",
            metadata={"detail": "test"},
        )
    )

    await recorder.flush(run_context)
