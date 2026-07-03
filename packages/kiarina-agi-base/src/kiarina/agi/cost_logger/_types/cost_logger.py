from typing import Protocol, runtime_checkable

from kiarina.agi.cost_record import CostRecord

from .cost_logger_name import CostLoggerName


@runtime_checkable
class CostLogger(Protocol):
    name: CostLoggerName

    def log_cost_add(self, cost_record: CostRecord) -> None: ...

    def log_cost_flush(self, cost_records: list[CostRecord]) -> None: ...
