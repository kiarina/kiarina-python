from typing import Any

from kiarina.agi.base.run_context import RunContext

from .._schemas.request_log_entry import RequestLogEntry
from .._types.request_logger import RequestLogger
from .._types.request_logger_name import RequestLoggerName


class BaseRequestLogger(RequestLogger):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: RequestLoggerName | None = None

    @property
    def name(self) -> RequestLoggerName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Request logger name not set")

        return self._name

    @name.setter
    def name(self, value: RequestLoggerName) -> None:
        self._name = value

    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None:
        pass

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,
        *,
        run_context: RunContext,
    ) -> None:
        pass
