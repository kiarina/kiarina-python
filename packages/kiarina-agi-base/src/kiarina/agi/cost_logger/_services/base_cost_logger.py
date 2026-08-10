import logging
from dataclasses import dataclass

from kiarina.agi.cost_record import CostKind, CostRecord, CostSource, Microdollars
from kiarina.agi.cost_utils import format_cost
from kiarina.currency import CurrencyCode

from .._settings import settings_manager
from .._types.cost_logger import CostLogger
from .._types.cost_logger_name import CostLoggerName

logger = logging.getLogger(__name__)


@dataclass
class _Aggregates:
    count: int = 0
    total_cost: Microdollars = 0


class BaseCostLogger(CostLogger):
    def __init__(self) -> None:
        self._name: CostLoggerName | None = None

    @property
    def name(self) -> CostLoggerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Cost logger name not set")

        return self._name

    @name.setter
    def name(self, value: CostLoggerName) -> None:
        self._name = value

    @property
    def currency(self) -> CurrencyCode | None:
        return settings_manager.get_settings().currency

    @property
    def exchange_rate(self) -> float | None:
        return settings_manager.get_settings().exchange_rate

    @property
    def decimal_places(self) -> int | None:
        return settings_manager.get_settings().decimal_places

    def log_cost_add(self, cost_record: CostRecord) -> None:
        pass

    def log_cost_flush(self, cost_records: list[CostRecord]) -> None:
        pass

    def _aggregate(
        self,
        cost_records: list[CostRecord],
    ) -> dict[CostKind, dict[CostSource, _Aggregates]]:
        kind_source_cost_map: dict[CostKind, dict[CostSource, _Aggregates]] = {}

        for record in cost_records:
            if record.kind not in kind_source_cost_map:
                kind_source_cost_map[record.kind] = {}

            if record.source not in kind_source_cost_map[record.kind]:
                kind_source_cost_map[record.kind][record.source] = _Aggregates()

            kind_source_cost_map[record.kind][record.source].count += 1
            kind_source_cost_map[record.kind][
                record.source
            ].total_cost += record.microdollars

        return kind_source_cost_map

    def _format_cost(self, microdollars: int) -> str:
        return format_cost(
            microdollars,
            currency=self.currency,
            exchange_rate=self.exchange_rate,
            decimal_places=self.decimal_places,
        )
