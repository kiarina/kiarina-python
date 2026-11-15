import pytest

from kiarina.agi.chat_provider import ChatProviderContext
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


def test_add_cost_record(run_context: RunContext, cost_recorder: CostRecorder) -> None:
    ctx = ChatProviderContext.create(
        cost_recorder=cost_recorder, run_context=run_context
    )
    assert ctx.cost_record is None

    record = CostRecord(microdollars=12, kind="chat", source="example")
    ctx.add_cost_record(record)
    assert ctx.cost_record is record
    assert cost_recorder.records == [record]

    with pytest.raises(RuntimeError, match="one cost"):
        ctx.add_cost_record(CostRecord(kind="chat", source="example"))
    assert cost_recorder.records == [record]
