from typing import TypeAlias

import pytest
from langchain.tools import tool
from pydantic import BaseModel, Field, ValidationError

from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.langchain_tool import LangChainTool
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolContext

LCOutputItem: TypeAlias = str | dict[str, str]
LCOutput: TypeAlias = (
    str | list[LCOutputItem] | tuple[str, dict[str, str]] | tuple[str, str] | int
)


@tool
def hello() -> str:
    """Say hello"""
    return "Hello"


class AddNumbersSchema(BaseModel):
    a: int = Field(..., description="First number")
    b: int = Field(..., description="Second number")


@tool(args_schema=AddNumbersSchema, return_direct=True)
def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@pytest.fixture
def ctx(run_context: RunContext) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="hello"),
        run_context=run_context,
    )


def test_init() -> None:
    lc_tool = LangChainTool(hello)

    assert lc_tool.name == "hello"
    assert isinstance(lc_tool.tool_schema, type)
    assert issubclass(lc_tool.tool_schema, BaseModel)


def test_to_tool_info_no_args_schema() -> None:
    lc_tool = LangChainTool(hello)
    tool_info = lc_tool.to_tool_info()

    assert tool_info.name == "hello"
    assert tool_info.description == "Say hello"
    assert tool_info.args_schema is not None

    print(tool_info.model_dump_json(indent=2))


def test_to_tool_info_with_args_schema() -> None:
    lc_tool = LangChainTool(add_numbers)
    tool_info = lc_tool.to_tool_info()

    assert tool_info.name == "add_numbers"
    assert tool_info.description == "Add two numbers"
    assert tool_info.args_schema is not None

    print(tool_info.model_dump_json(indent=2))


async def test_run(ctx: ToolContext) -> None:

    @tool
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    lc_tool = LangChainTool(add_numbers)

    ctx.tool_call.name = "add_numbers"
    ctx.tool_call.args = {"a": 2, "b": 3}

    events = [event async for event in lc_tool.run(ctx)]

    assert len(events) == 1
    event = events[0]
    assert event.type == "tool_message"
    assert isinstance(event, ToolMessageEvent)

    print(event.to_text())


async def test_run_invalid_args(ctx: ToolContext) -> None:

    @tool
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    lc_tool = LangChainTool(add_numbers)

    ctx.tool_call.name = "add_numbers"
    ctx.tool_call.args = {"a": "not a number", "b": 3}

    with pytest.raises(ValidationError):
        [event async for event in lc_tool.run(ctx)]


@pytest.mark.parametrize(
    "output",
    [
        pytest.param("Hello", id="1. string"),
        pytest.param(["Hello", "World"], id="2. list of strings"),
        pytest.param(("Hello", {"key": "value"}), id="3. tuple of (content, artifact)"),
        pytest.param(("Hello", "not a dict"), id="4. tuple with non-dict artifact"),
        pytest.param(123, id="5. non-string, non-list, non-tuple output"),
    ],
)
async def test_parse_output(ctx: ToolContext, output: LCOutput) -> None:

    @tool
    def return_output() -> LCOutput:
        """Return the provided output"""
        return output

    lc_tool = LangChainTool(return_output)
    ctx.tool_call.name = "return_output"

    events = [event async for event in lc_tool.run(ctx)]

    assert len(events) == 1
    event = events[0]
    assert event.type == "tool_message"

    print(event.to_text())


@pytest.mark.parametrize(
    "output",
    [
        pytest.param("Hello", id="1. string"),
        pytest.param(
            ["Hello", {"type": "text", "text": "Hello"}, {"type": "unknown"}],
            id="2. list of strings and dicts",
        ),
    ],
)
async def test_to_contents(ctx: ToolContext, output: LCOutput) -> None:
    @tool
    def return_output() -> LCOutput:
        """Return the provided output"""
        return output

    lc_tool = LangChainTool(return_output, raw_output=True)
    ctx.tool_call.name = "return_output"

    events = [event async for event in lc_tool.run(ctx)]

    assert len(events) == 1
    event = events[0]
    assert event.type == "tool_message"

    print(event.to_text())
