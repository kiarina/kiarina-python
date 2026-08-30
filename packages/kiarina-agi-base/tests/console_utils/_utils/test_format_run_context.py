from kiarina.agi.console_utils import format_run_context
from kiarina.agi.run_context import RunContext


def test_format_run_context_uses_timezone(run_context: RunContext) -> None:
    output = format_run_context(
        run_context.model_copy(update={"timezone": "Asia/Tokyo"})
    )

    assert "timezone: Asia/Tokyo" in output
    assert "time_zone:" not in output
