import pytest

from kiarina.agi.tool import ToolContext, tool_registry


async def test_exit_tool(ctx: ToolContext) -> None:
    tool = tool_registry.create("exit")

    ctx.tool_call.name = "exit"
    ctx.tool_call.args = {"message": "Critical error occurred", "code": 7}

    with pytest.raises(SystemExit):
        [event async for event in tool.run(ctx)]
