import asyncio
import json

import pytest
from pydantic import BaseModel, Field

from kiarina.agi.agent import run_agent
from kiarina.agi.agent._types.agent_options import AgentOptions
from kiarina.agi.event import AIMessageEvent, Event, ToolMessageEvent
from kiarina.agi.history import History
from kiarina.agi.message import AIMessage, HumanMessage, ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import Tool, ToolOptions, tool


class HelloSchema(BaseModel):
    """Say hello"""

    name: str = Field(description="The name to greet")


@tool(tool_schema=HelloSchema)
def HelloTool(name: str) -> str:
    return f"Hello, {name}!"


@pytest.fixture
def hello_tool() -> Tool:
    hello = HelloTool()
    hello.name = "hello"
    return hello


@pytest.fixture
def history(hello_tool: Tool) -> History:
    return History(tool_infos=[hello_tool.to_tool_info()])


@pytest.fixture
def tool_call_human_message_event() -> HumanMessage:
    return HumanMessage.create(
        json.dumps(
            {
                "content": "Say hello to Alice",
                "tool_calls": [
                    {
                        "name": "hello",
                        "args": {"name": "Alice"},
                    }
                ],
            }
        )
    )


@pytest.fixture
def tool_options() -> ToolOptions:
    hello = HelloTool()
    hello.name = "hello"

    return {"tools": [hello]}


async def test_run_agent_workflow(
    history: History,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(HumanMessage.create("Hello"))
    events = [
        event
        async for event in run_agent(
            history, tool_options=tool_options, run_context=run_context
        )
    ]

    assert len(events) == 1
    assert isinstance(events[0], AIMessageEvent)


async def test_run_agent_tool(
    history: History,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(
        AIMessage.create(tool_calls=[ToolCall(name="hello", args={"name": "Alice"})])
    )

    agent_options: AgentOptions = {"until_tool_runs": ["hello"]}

    events = [
        event
        async for event in run_agent(
            history,
            tool_options=tool_options,
            agent_options=agent_options,
            run_context=run_context,
        )
    ]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert events[0].to_text() == "Hello, Alice!"


async def test_is_conversation_end(
    history: History,
    tool_call_human_message_event: HumanMessage,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(tool_call_human_message_event)
    agent_options: AgentOptions = {"max_iterations": 10}
    events = [
        event
        async for event in run_agent(
            history,
            tool_options=tool_options,
            agent_options=agent_options,
            run_context=run_context,
        )
    ]

    assert len(events) == 3
    assert isinstance(events[0], AIMessageEvent)
    assert len(events[0].message.tool_calls) == 1
    assert isinstance(events[1], ToolMessageEvent)
    assert isinstance(events[2], AIMessageEvent)
    assert len(events[2].message.tool_calls) == 0


async def test_until_end(
    history: History,
    tool_call_human_message_event: HumanMessage,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(tool_call_human_message_event)

    agent_options: AgentOptions = {
        "max_iterations": 1,
        "until_end": True,
    }

    events = [
        event
        async for event in run_agent(
            history,
            tool_options=tool_options,
            agent_options=agent_options,
            run_context=run_context,
        )
    ]

    assert len(events) == 2
    assert isinstance(events[0], AIMessageEvent)
    assert len(events[0].message.tool_calls) == 1
    assert isinstance(events[1], ToolMessageEvent)


async def test_until_tool_calls(
    history: History,
    tool_call_human_message_event: HumanMessage,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(tool_call_human_message_event)

    agent_options: AgentOptions = {
        "max_iterations": 10,
        "until_tool_calls": ["hello"],
    }

    events = [
        event
        async for event in run_agent(
            history,
            tool_options=tool_options,
            agent_options=agent_options,
            run_context=run_context,
        )
    ]

    assert len(events) == 1
    assert isinstance(events[0], AIMessageEvent)
    assert len(events[0].message.tool_calls) == 1


async def test_until_tool_runs(
    history: History,
    tool_call_human_message_event: HumanMessage,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(tool_call_human_message_event)

    agent_options: AgentOptions = {
        "max_iterations": 10,
        "until_tool_runs": ["hello"],
    }

    events = [
        event
        async for event in run_agent(
            history,
            tool_options=tool_options,
            agent_options=agent_options,
            run_context=run_context,
        )
    ]

    assert len(events) == 2
    assert isinstance(events[0], AIMessageEvent)
    assert len(events[0].message.tool_calls) == 1
    assert isinstance(events[1], ToolMessageEvent)


async def test_missing_tools(
    history: History,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(
        AIMessage.create(tool_calls=[ToolCall(name="missing", args={"name": "Alice"})])
    )

    events = [
        event
        async for event in run_agent(
            history, tool_options=tool_options, run_context=run_context
        )
    ]
    assert events == []


async def test_stop_event(
    history: History,
    tool_call_human_message_event: HumanMessage,
    tool_options: ToolOptions,
    run_context: RunContext,
) -> None:
    history.add_message(tool_call_human_message_event)
    stop_event = asyncio.Event()
    events: list[Event] = []
    agent_options: AgentOptions = {"max_iterations": 10}

    async for event in run_agent(
        history,
        tool_options=tool_options,
        agent_options=agent_options,
        run_context=run_context,
        stop_event=stop_event,
    ):
        events.append(event)
        stop_event.set()

    assert len(events) == 1
    assert isinstance(events[0], AIMessageEvent)
