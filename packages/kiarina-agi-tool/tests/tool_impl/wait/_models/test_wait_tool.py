from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.tool import ToolContext, tool_registry


async def test_wait_tool(ctx: ToolContext) -> None:
    tool = tool_registry.create("wait")

    ctx.tool_call.name = "wait"
    ctx.tool_call.args = {"wait_time": 0}

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].message.contents[0].text == "Waited for 0.0 seconds."
