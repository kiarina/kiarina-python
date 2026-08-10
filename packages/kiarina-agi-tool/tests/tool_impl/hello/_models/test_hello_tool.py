from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.tool import ToolContext, tool_registry


async def test_hello_tool(ctx: ToolContext) -> None:
    tool = tool_registry.create("hello")
    ctx.tool_call.name = "hello"

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].message.contents[0].text == "Hello"
