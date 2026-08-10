import sys

from kiarina.agi.console_utils import divider, section_header
from kiarina.agi.request_logger import BaseRequestLogger, RequestLogEntry
from kiarina.agi.run_context import RunContext


class ConsoleRequestLogger(BaseRequestLogger):
    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None:
        print(
            self._format(log_entry, f"REQUEST SUCCESS: {log_entry.kind}"),
            flush=True,
            file=sys.stderr,
        )

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,
        *,
        run_context: RunContext,
    ) -> None:
        print(
            self._format(log_entry, f"REQUEST ERROR: {log_entry.kind}"),
            flush=True,
            file=sys.stderr,
        )

    def _format(self, log_entry: RequestLogEntry, title: str) -> str:
        lines = [
            "",
            section_header(title),
            f"source: {log_entry.source}",
            f"created_at: {log_entry.created_at.isoformat()}",
        ]

        for k, v in log_entry.metadata.items():
            lines.append(f"{k}: {v}")

        lines.append(divider())
        lines.append("")
        lines.append(log_entry.content)

        return "\n".join(lines)
