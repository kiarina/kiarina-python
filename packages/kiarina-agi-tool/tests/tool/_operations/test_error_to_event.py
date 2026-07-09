import asyncio

import pytest
from pydantic import BaseModel, Field

from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolContext, ToolError, tool
from kiarina.agi.tool._operations.error_to_event import error_to_event


class HelloSchema(BaseModel):
    name: str = Field(description="The name to greet.")


@tool(tool_schema=HelloSchema)
def HelloTool(name: str) -> str:
    "Says hello"
    return f"Hello {name}"


@pytest.fixture
def ctx(run_context: RunContext) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="hello", args={"name": "Alice"}),
        run_context=run_context,
    )


def test_tool_error(ctx: ToolContext) -> None:
    e = ToolError("Something went wrong.")
    event = error_to_event(ctx, HelloTool(), e)

    assert isinstance(event, ToolMessageEvent)
    assert event.message.tool_call_id == ctx.tool_call.id
    assert event.message.tool_name == ctx.tool_call.name
    assert len(event.message.contents) == 1
    assert "Something went wrong." in event.to_text()

    print(event.model_dump_json(indent=2))
    print("---")
    print(event.to_text())


def test_cancelled_error(ctx: ToolContext) -> None:
    e = asyncio.CancelledError()
    event = error_to_event(ctx, HelloTool(), e)

    assert isinstance(event, ToolMessageEvent)
    assert len(event.message.contents) == 1
    assert "Tool execution was cancelled by the user." in event.to_text()

    print(event.model_dump_json(indent=2))
    print("---")
    print(event.to_text())


def test_generic_error(ctx: ToolContext) -> None:
    e = ValueError("Invalid value.")
    event = error_to_event(ctx, HelloTool(), e)

    assert isinstance(event, ToolMessageEvent)
    assert len(event.message.contents) == 1
    assert "ValueError: Invalid value." in event.to_text()

    print(event.model_dump_json(indent=2))
    print("---")
    print(event.to_text())
