import asyncio
from collections.abc import Iterator
from typing import TypedDict

import pytest
from pydantic import BaseModel, Field

from kiarina.agi.event import CustomEvent, ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.post_hook import PostHookContext, posthook
from kiarina.agi.pre_hook import PreHookContext, prehook
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolError, ToolNotFoundError, ToolOptions, run_tool, tool


class RunToolKwargs(TypedDict):
    tool_options: ToolOptions
    run_context: RunContext


@prehook
def HelloPreHook(ctx: PreHookContext) -> None:
    print("HelloPreHook run")


@posthook
def HelloPostHook(ctx: PostHookContext) -> None:
    print("HelloPostHook run")


class HelloSchema(BaseModel):
    """Say hello"""

    name: str = Field(description="The name to greet")


@tool(tool_schema=HelloSchema)
def HelloTool(name: str) -> str:
    return f"Hello, {name}!"


@tool(tool_schema=HelloSchema)
async def CancelledTool(name: str) -> str:
    raise asyncio.CancelledError()


@tool(tool_schema=HelloSchema)
def ErrorTool(name: str) -> str:
    raise ToolError(f"Error: invalid name `{name}`")


# --------------------------------------------------
# Fixtures
# --------------------------------------------------


@pytest.fixture(autouse=True)
def setup_pre_hook_settings() -> Iterator[None]:
    from kiarina.agi.pre_hook import settings_manager

    settings_manager.cli_args = {
        "customs": {
            "hello_pre": f"{__name__}:HelloPreHook",
        }
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
def setup_post_hook_settings() -> Iterator[None]:
    from kiarina.agi.post_hook import settings_manager

    settings_manager.cli_args = {
        "customs": {
            "hello_post": f"{__name__}:HelloPostHook",
        }
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
def setup_tool_settings() -> Iterator[None]:
    from kiarina.agi.tool import settings_manager

    settings_manager.cli_args = {
        "customs": {
            "hello": f"{__name__}:HelloTool",
        },
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def kwargs(run_context: RunContext) -> RunToolKwargs:
    cancelled = CancelledTool()
    cancelled.name = "cancelled"

    error = ErrorTool()
    error.name = "error"

    hello_pre_hook = HelloPreHook()
    hello_pre_hook.name = "hello_pre"

    hello_post_hook = HelloPostHook()
    hello_post_hook.name = "hello_post"

    return {
        "tool_options": {
            "tools": ["hello", cancelled, error],
            "pre_hooks": [
                hello_pre_hook,
                {"hook": "hello_pre", "apply_to": ["hello"]},
                "hello_pre",
                "hello_pre@hello",
            ],
            "post_hooks": [
                hello_post_hook,
                {"hook": "hello_post", "apply_to": ["hello"]},
                "hello_post",
                "hello_post@hello",
            ],
        },
        "run_context": run_context,
    }


# --------------------------------------------------
# Tests
# --------------------------------------------------


async def test_no_target(kwargs: RunToolKwargs) -> None:
    tool_call = ToolCall(name="missing")

    with pytest.raises(ToolNotFoundError, match="Tool not found: missing"):
        [event async for event in run_tool(tool_call, **kwargs)]


async def test_executed(kwargs: RunToolKwargs) -> None:
    tool_call = ToolCall(name="hello", args={"name": "Alice"})
    events = [event async for event in run_tool(tool_call, **kwargs)]
    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].to_text() == "Hello, Alice!"
    print(events[0].to_text())


async def test_cancelled(kwargs: RunToolKwargs) -> None:
    tool_call = ToolCall(name="cancelled", args={"name": "Eve"})
    events = [event async for event in run_tool(tool_call, **kwargs)]
    assert len(events) == 2
    assert isinstance(events[0], CustomEvent)
    assert events[0].payload["type"] == "tool_cancelled"
    assert isinstance(events[1], ToolMessageEvent)
    assert events[1].message.failed
    assert "Tool execution was cancelled by the user." in events[1].to_text()
    print(events[1].to_text())


async def test_tool_error(kwargs: RunToolKwargs) -> None:
    tool_call = ToolCall(name="error", args={"name": "Dave"})
    events = [event async for event in run_tool(tool_call, **kwargs)]
    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].message.failed
    assert "Tool execution failed." in events[0].to_text()
    assert "Error: invalid name `Dave`" in events[0].to_text()
    print(events[0].to_text())
