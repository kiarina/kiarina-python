from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder


async def test_null_cost_recorder(run_context: Any) -> None:
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
