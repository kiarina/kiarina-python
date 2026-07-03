from typing import Any

from kiarina.agi.base.cost_logger import CostLogger, cost_logger_registry
from kiarina.agi.base.cost_record import CostRecord
from kiarina.agi.base.run_context import RunContext

from .._types.cost_recorder import CostRecorder
from .._types.cost_recorder_name import CostRecorderName


class BaseCostRecorder(CostRecorder):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self.records: list[CostRecord] = []
        self._logger: CostLogger | None = None
        self._name: CostRecorderName | None = None

    @property
    def name(self) -> CostRecorderName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Cost recorder name not set")

        return self._name

    @name.setter
    def name(self, value: CostRecorderName) -> None:
        self._name = value

    @property
    def total_microdollars(self) -> int:
        return sum(record.microdollars for record in self.records)

    @property
    def total_dollars(self) -> float:
        return self.total_microdollars / 1_000_000.0

    @property
    def logger(self) -> CostLogger:
        if self._logger is None:
            self._logger = cost_logger_registry.resolve()

        return self._logger

    def add(self, cost_record: CostRecord) -> None:
        self.records.append(cost_record)
        self.logger.log_cost_add(cost_record)

    def clear(self) -> None:
        self.records.clear()

    async def flush(self, run_context: RunContext) -> None:
        if not self.records:
            return

        await self._save(run_context)
        self.logger.log_cost_flush(self.records)
        self.clear()

    async def _save(self, run_context: RunContext) -> None: ...
