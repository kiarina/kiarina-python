from typing import Protocol, runtime_checkable

from kiarina.agi.base.cost_record import CostRecord
from kiarina.agi.base.run_context import RunContext

from .cost_recorder_name import CostRecorderName


@runtime_checkable
class CostRecorder(Protocol):
    name: CostRecorderName
    records: list[CostRecord]

    @property
    def total_microdollars(self) -> int: ...

    @property
    def total_dollars(self) -> float: ...

    def add(self, cost_record: CostRecord) -> None: ...

    def clear(self) -> None: ...

    async def flush(self, run_context: RunContext) -> None: ...
