import pytest

from kiarina.agi.content import Content
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolContext, tool
from kiarina.agi.tool._operations.output_to_event import output_to_event


@tool
def HelloTool() -> str:
    "Says hello"
    return "Hello"


@pytest.fixture
def ctx(run_context: RunContext) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="hello"),
        run_context=run_context,
    )


def test_event(ctx: ToolContext) -> None:
    event = ToolMessageEvent.create("Hello", tool_name="hello", tool_call_id="1")

    assert output_to_event(ctx, HelloTool(), event) is event


def test_message(ctx: ToolContext) -> None:
    message = ToolMessage(tool_name="hello", tool_call_id="1")

    event = output_to_event(ctx, HelloTool(), message)

    assert isinstance(event, ToolMessageEvent)
    assert event.message is message


def test_content(ctx: ToolContext) -> None:
    content = Content(text="Hello")

    event = output_to_event(ctx, HelloTool(), content)

    assert isinstance(event, ToolMessageEvent)
    assert event.message.tool_call_id == ctx.tool_call.id
    assert event.message.tool_name == ctx.tool_call.name
    assert len(event.message.contents) == 1
    assert event.message.contents[0] is content


def test_str(ctx: ToolContext) -> None:
    event = output_to_event(ctx, HelloTool(), "Hello")

    assert isinstance(event, ToolMessageEvent)
    assert event.message.tool_call_id == ctx.tool_call.id
    assert event.message.tool_name == ctx.tool_call.name
    assert len(event.message.contents) == 1
    assert event.message.contents[0].text == "Hello"
