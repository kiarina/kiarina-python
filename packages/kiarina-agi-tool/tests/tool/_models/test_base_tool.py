from collections.abc import AsyncIterator, Iterator

import pytest
from pydantic import BaseModel, Field, ValidationError

from kiarina.agi.event import CustomEvent, ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import (
    AdditionalFieldConfig,
    BaseTool,
    ToolContext,
    ToolOutput,
    settings_manager,
)
from kiarina.i18n import I18n, catalog


class AddNumbersSchema(I18n, scope="kiarina_agi_tests"):
    """Add two numbers"""

    a: int = Field(description="The first number")
    b: int = Field(description="The second number")


class AddNumbersTool(BaseTool):
    tool_schema = AddNumbersSchema

    def _run(self, a: int, b: int) -> str:
        return str(a + b)


class AsyncAddNumbersTool(BaseTool):
    tool_schema = AddNumbersSchema

    async def _run(self, a: int, b: int) -> str:
        return str(a + b)


class AsyncIteratorAddNumbersTool(BaseTool):
    tool_schema = AddNumbersSchema

    async def _run(self, a: int, b: int) -> AsyncIterator[ToolOutput]:
        yield CustomEvent(payload={"state": "progress"})
        yield str(a + b)


@pytest.fixture(autouse=True)
def setup_i18n() -> Iterator[None]:
    catalog.add_from_dict(
        {
            "ja": {
                "kiarina_agi_tests": {
                    "__doc__": "2つの数字を足す",
                    "a": "最初の数字",
                    "b": "次の数字",
                    "reason": "理由",
                }
            }
        }
    )
    yield
    catalog.clear()


@pytest.fixture(autouse=True)
def setup_tool_settings() -> Iterator[None]:
    settings_manager.cli_args = {
        "additional_fields": [
            AdditionalFieldConfig(
                name="reason",
                type_hint="str",
                description="Reason for calling the tool",
                i18n_scope="kiarina_agi_tests",
                i18n_key="reason",
                apply_to=["add_numbers"],
            )
        ]
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def ctx(run_context: RunContext) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="hello"),
        run_context=run_context,
    )


def test_str() -> None:
    add_numbers = AddNumbersTool()
    add_numbers.name = "add_numbers"
    assert str(add_numbers) == "AddNumbersTool"


async def test_name() -> None:
    add_numbers = AddNumbersTool()
    add_numbers.name = "add_numbers"
    print(add_numbers.name)


# --------------------------------------------------
# to_tool_info
# --------------------------------------------------


async def test_to_tool_info() -> None:
    add_numbers = AddNumbersTool()
    add_numbers.name = "add_numbers"

    tool_info = add_numbers.to_tool_info(language="ja")

    assert tool_info.name == "add_numbers"
    assert tool_info.description == "2つの数字を足す"
    assert tool_info.args_schema["properties"]["a"]["description"] == "最初の数字"
    assert tool_info.args_schema["properties"]["b"]["description"] == "次の数字"
    assert tool_info.args_schema["properties"]["reason"]["description"] == "理由"

    print(tool_info.model_dump_json(indent=2))


# --------------------------------------------------
# run
# --------------------------------------------------


async def test_run_sync_func(ctx: ToolContext) -> None:
    add_numbers = AddNumbersTool()
    add_numbers.name = "add_numbers"

    ctx.tool_call.name = add_numbers.name
    ctx.tool_call.args = {"a": 1, "b": 2}

    events = [event async for event in add_numbers.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    print(events[0].model_dump_json(indent=2))


async def test_run_async_func(ctx: ToolContext) -> None:
    add_numbers = AsyncAddNumbersTool()
    add_numbers.name = "add_numbers"

    ctx.tool_call.name = add_numbers.name
    ctx.tool_call.args = {"a": 1, "b": 2}

    events = [event async for event in add_numbers.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    print(events[0].model_dump_json(indent=2))


async def test_run_async_iterator(ctx: ToolContext) -> None:
    add_numbers = AsyncIteratorAddNumbersTool()
    add_numbers.name = "add_numbers"

    ctx.tool_call.name = add_numbers.name
    ctx.tool_call.args = {"a": 1, "b": 2}

    events = [event async for event in add_numbers.run(ctx)]

    assert len(events) == 2
    assert isinstance(events[0], CustomEvent)
    assert isinstance(events[1], ToolMessageEvent)
    assert events[0].payload == {"state": "progress"}
    print(events[1].model_dump_json(indent=2))


# --------------------------------------------------
# _validate_tool_call_args
# --------------------------------------------------


async def test_validate_tool_call_args(ctx: ToolContext) -> None:
    add_numbers = AddNumbersTool()
    add_numbers.name = "add_numbers"

    ctx.tool_call.name = add_numbers.name
    ctx.tool_call.args = {"a": 1, "c": 2}

    with pytest.raises(ValidationError):
        try:
            [event async for event in add_numbers.run(ctx)]
        except ValidationError as e:
            print(e)
            raise


async def test_validate_tool_call_args_nested(ctx: ToolContext) -> None:

    class NestedArgs(BaseModel):
        value: int

    class NestedSchema(BaseModel):
        """Use nested args"""

        nested: NestedArgs

    class NestedTool(BaseTool):
        tool_schema = NestedSchema

        def _run(self, nested: NestedArgs) -> str:
            assert isinstance(nested, NestedArgs)
            return str(nested.value)

    nested = NestedTool()
    nested.name = "nested"

    ctx.tool_call.name = nested.name
    ctx.tool_call.args = {"nested": {"value": 7}}

    events = [event async for event in nested.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].message.contents[0].text == "7"


# --------------------------------------------------
# Use cases
# --------------------------------------------------


async def test_run_with_ctx(ctx: ToolContext) -> None:

    class WithCtxTool(BaseTool):
        tool_schema = AddNumbersSchema
        accepts_ctx = True

        def _run(self, ctx: ToolContext, a: int, b: int) -> str:
            return ctx.tool_call.name + ":" + str(a + b)

    with_ctx = WithCtxTool()
    with_ctx.name = "add_numbers"

    ctx.tool_call.name = with_ctx.name
    ctx.tool_call.args = {"a": 1, "b": 2}

    events = [event async for event in with_ctx.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].message.contents[0].text == "add_numbers:3"
