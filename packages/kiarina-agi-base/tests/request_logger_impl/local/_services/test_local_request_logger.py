import traceback

from kiarina.agi.request_logger import RequestLogEntry
from kiarina.agi.request_logger_impl.local import LocalRequestLogger
from kiarina.agi.run_context import RunContext


async def test_log_request_success(run_context: RunContext) -> None:
    logger = LocalRequestLogger()

    await logger.log_request_success(
        RequestLogEntry(
            kind="test",
            source="test",
            content="Hello",
            metadata={"test_key": "test_value"},
        ),
        run_context=run_context,
    )


async def test_log_request_error(run_context: RunContext) -> None:
    logger = LocalRequestLogger()

    try:
        _raise_test_exception()

    except Exception as e:
        await logger.log_request_error(
            RequestLogEntry(
                kind="test",
                source="test",
                content=f"{type(e)}: {e}\n\n{traceback.format_exc()}",
                metadata={"test_key": "test_value"},
            ),
            e,
            run_context=run_context,
        )


def _raise_test_exception() -> None:
    raise ValueError("This is a test exception for logging.")
