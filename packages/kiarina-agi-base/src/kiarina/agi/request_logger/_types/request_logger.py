from typing import Protocol, runtime_checkable

from kiarina.agi.run_context import RunContext

from .._schemas.request_log_entry import RequestLogEntry
from .request_logger_name import RequestLoggerName


@runtime_checkable
class RequestLogger(Protocol):
    name: RequestLoggerName

    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None: ...

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,  # Available for implementations that need direct access
        *,
        run_context: RunContext,
    ) -> None: ...
