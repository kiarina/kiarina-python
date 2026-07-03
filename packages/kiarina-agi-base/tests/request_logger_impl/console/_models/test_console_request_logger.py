import traceback

from kiarina.agi.base.request_logger import RequestLogEntry
from kiarina.agi.base.request_logger_impl.console import ConsoleRequestLogger


async def test_log_request_success(run_context) -> None:
    logger = ConsoleRequestLogger()

    await logger.log_request_success(
        RequestLogEntry(
            kind="test",
            source="test",
            content="Hello",
            metadata={"test_key": "test_value"},
        ),
        run_context=run_context,
    )


async def test_log_request_error(run_context) -> None:
    logger = ConsoleRequestLogger()

    def _raise_test_exception() -> None:
        raise ValueError("This is a test exception for logging.")

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
