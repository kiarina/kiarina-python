from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.tool import ToolContext, tool_registry


async def test_finish_tool(ctx: ToolContext) -> None:
    tool = tool_registry.create("finish")
    ctx.tool_call.name = "finish"
    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].message.return_direct is True

    print(events[0].model_dump_json(indent=2))
