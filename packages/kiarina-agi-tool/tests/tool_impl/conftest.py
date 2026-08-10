import pytest

from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolContext


@pytest.fixture
def ctx(run_context: RunContext) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="hello"),
        run_context=run_context,
    )
