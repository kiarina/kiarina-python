import sys

from kiarina.agi.console_utils import divider, section_header, stderr_color
from kiarina.agi.cost_logger import BaseCostLogger
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_utils import format_cost


class ConsoleCostLogger(BaseCostLogger):
    def log_cost_add(self, cost_record: CostRecord) -> None:
        with stderr_color("black"):
            print(self._format_add(cost_record), flush=True, file=sys.stderr)

    def log_cost_flush(self, cost_records: list[CostRecord]) -> None:
        with stderr_color("black"):
            print(self._format_flush(cost_records), flush=True, file=sys.stderr)

    def _format_add(self, cost_record: CostRecord) -> str:
        cost = self._format_cost(cost_record.microdollars)

        lines = [
            "",
            "",
            section_header(f"{cost_record.kind.upper()} COST: {cost}"),
            f"kind: {cost_record.kind}",
            f"source: {cost_record.source}",
        ]

        for key, value in cost_record.metadata.items():
            if value:
                lines.append(f"{key}: {value}")

        lines.append(divider())

        return "\n".join(lines)

    def _format_flush(self, cost_records: list[CostRecord]) -> str:
        total_cost = format_cost(
            sum(record.microdollars for record in cost_records),
            currency=self.currency,
            exchange_rate=self.exchange_rate,
            decimal_places=self.decimal_places,
        )

        lines = [
            "",
            "",
            section_header(f"TOTAL COSTS: {total_cost}"),
        ]

        for kind, source_map in self._aggregate(cost_records).items():
            lines.append(f"{kind}:")

            for source, aggregates in source_map.items():
                lines.append(
                    f"  {source}: {aggregates.count} calls, {self._format_cost(aggregates.total_cost)}"
                )

        lines.append(divider())

        return "\n".join(lines)
