from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from kiarina.agi.agent import BaseAgent, MissingToolsError
from kiarina.agi.agent._schemas.agent_context import AgentContext
from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.event import (
    AIMessageEvent,
    CustomEvent,
    Event,
    HumanMessageEvent,
    ToolMessageEvent,
)
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolNotFoundError


class MyAgent(BaseAgent):
    async def _pre_run(
        self, ctx: AgentContext, history: History
    ) -> AsyncIterator[Event]:
        yield CustomEvent.create(type="pre_run")

    async def _run_workflow(
        self,
        ctx: AgentContext,
        history: History,
    ) -> AsyncIterator[Event]:
        yield AIMessageEvent.create("workflow")

    async def _run_tool(
        self,
        ctx: AgentContext,
        history: History,
        tool_call: ToolCall,
    ) -> AsyncIterator[Event]:
        if tool_call.name == "missing":
            raise ToolNotFoundError(tool_call.name)

        yield ToolMessageEvent.create(
            f"tool:{tool_call.name}",
            tool_name=tool_call.name,
            tool_call_id=tool_call.id,
        )

    async def post_run(
        self, ctx: AgentContext, history: History
    ) -> AsyncIterator[Event]:
        yield CustomEvent.create(type="post_run")


@pytest.fixture
def agent() -> MyAgent:
    agent = MyAgent(hello="world")
    agent.name = "my"
    return agent


@pytest.fixture
def ctx(run_context: RunContext) -> AgentContext:
    return AgentContext.create(run_context=run_context)


@pytest.fixture
def history() -> History:
    return History()


async def test_base_agent(agent: BaseAgent) -> None:
    assert agent.init_kwargs == {"hello": "world"}
    assert agent.name == "my"
    assert str(agent) == "MyAgent"


# --------------------------------------------------
# pre_run
# --------------------------------------------------


async def test_pre_run(agent: BaseAgent, ctx: AgentContext, history: History) -> None:
    events = [event async for event in agent.pre_run(ctx, history)]

    assert len(events) == 1
    assert events[0].to_text() == "pre_run"
    assert history.events == []


async def test_prepare_file_infos(
    image_file_info: FileInfo,
    agent: BaseAgent,
    ctx: AgentContext,
    history: History,
) -> None:
    history.add_file_info(image_file_info)
    assert len(history.file_infos) == 1
    assert history.file_infos[0].asset_uri is None

    [_ async for _ in agent.pre_run(ctx, history)]
    assert len(history.file_infos) == 1
    assert history.file_infos[0].asset_uri is not None

    history.add_file_info(
        image_file_info.model_copy(
            update={"uri_or_file_path": history.file_infos[0].asset_uri}
        )
    )
    assert len(history.file_infos) == 2
    assert history.file_infos[1].asset_uri is None

    [_ async for _ in agent.pre_run(ctx, history)]
    assert len(history.file_infos) == 2
    assert history.file_infos[1].asset_uri is not None

    history.add_file_info(
        image_file_info.model_copy(update={"intermediate_file_path": "not_found"})
    )
    assert len(history.file_infos) == 3
    [_ async for _ in agent.pre_run(ctx, history)]
    assert len(history.file_infos) == 2


async def test_update_file_infos_only_updates_current_runner(
    tmp_path: Path,
    run_context: RunContext,
    agent: BaseAgent,
) -> None:
    current_file_path = tmp_path / "current.txt"
    current_file_path.write_text("current")
    other_file_path = tmp_path / "other.txt"
    other_file_path.write_text("other")

    current_file_info = await load_file_info(
        str(current_file_path),
        run_context=run_context,
    )
    other_file_info = await load_file_info(
        str(other_file_path),
        run_context=run_context,
    )
    assert current_file_info is not None
    assert other_file_info is not None

    other_file_info = other_file_info.model_copy(update={"node_id": "other"})

    history = History(file_infos=[current_file_info, other_file_info])

    current_file_path.unlink()
    other_file_path.unlink()

    [
        _
        async for _ in agent.pre_run(
            AgentContext.create(run_context=run_context), history
        )
    ]

    assert history.file_infos == [other_file_info]


async def test_update_file_infos_uses_local_node_id(
    tmp_path: Path,
    run_context: RunContext,
    agent: BaseAgent,
) -> None:
    current_file_path = tmp_path / "current.txt"
    current_file_path.write_text("current")

    current_file_info = await load_file_info(
        str(current_file_path),
        run_context=run_context,
    )
    assert current_file_info is not None

    ctx = AgentContext.create(
        run_context=run_context.model_copy(update={"node_id": "remote"})
    )
    history = History(file_infos=[current_file_info])

    current_file_path.unlink()

    [_ async for _ in agent.pre_run(ctx, history)]

    assert history.file_infos == []


async def test_update_file_infos_applies_file_limits(
    tmp_path: Path,
    test_data_dir: Path,
    run_context: RunContext,
    agent: BaseAgent,
) -> None:
    image_file_path = test_data_dir / "png" / "miineko_256x256_799b.png"
    copied_image_file_path = tmp_path / "sample2.png"
    copied_image_file_path.write_bytes(image_file_path.read_bytes())

    first_file_info = await load_file_info(
        str(image_file_path),
        run_context=run_context,
    )
    second_file_info = await load_file_info(
        str(copied_image_file_path),
        run_context=run_context,
    )
    assert first_file_info is not None
    assert second_file_info is not None

    ctx = AgentContext.create(
        file_limits=ChatLimits(image_file_count_limit=1),
        run_context=run_context,
    )
    history = History(file_infos=[first_file_info, second_file_info])

    [_ async for _ in agent.pre_run(ctx, history)]

    assert len(history.file_infos) == 1
    assert history.file_infos[0].type == "image"


# --------------------------------------------------
# run
# --------------------------------------------------


async def test_run_no_message(
    agent: BaseAgent, ctx: AgentContext, history: History
) -> None:
    with pytest.raises(ValueError, match="No message found in history"):
        [event async for event in agent.run(ctx, history)]


async def test_run_no_tool_calls(
    agent: BaseAgent,
    ctx: AgentContext,
    history: History,
) -> None:
    history.events = [AIMessageEvent.create("hello")]

    with pytest.raises(ValueError, match="Last AI message has no tool calls"):
        [event async for event in agent.run(ctx, history)]


async def test_run_missing_tools_raises(
    agent: BaseAgent,
    ctx: AgentContext,
    history: History,
) -> None:
    history.events = [
        AIMessageEvent.create(
            tool_calls=[
                ToolCall(id="tool-1", name="hello", args={"name": "Alice"}),
                ToolCall(id="tool-2", name="missing", args={"name": "Bob"}),
            ]
        ),
        ToolMessageEvent.create(
            tool_name="hello",
            tool_call_args={"name": "Alice"},
            tool_call_id="tool-1",
        ),
    ]

    with pytest.raises(MissingToolsError, match="Missing tools: missing"):
        [event async for event in agent.run(ctx, history)]


async def test_run_workflow(
    agent: BaseAgent, ctx: AgentContext, history: History
) -> None:
    history.events = [HumanMessageEvent.create("hello")]
    events = [event async for event in agent.run(ctx, history)]

    assert len(events) == 1
    assert events[0].to_text() == "workflow"
    assert history.get_messages()[-1].to_text() == "workflow"


async def test_run_tool(agent: BaseAgent, ctx: AgentContext, history: History) -> None:
    history.events = [
        AIMessageEvent.create(
            tool_calls=[
                ToolCall(id="tool-1", name="hello", args={"name": "Alice"}),
                ToolCall(id="tool-2", name="bye", args={"name": "Bob"}),
            ]
        ),
        ToolMessageEvent.create(
            tool_name="hello",
            tool_call_args={"name": "Alice"},
            tool_call_id="tool-1",
        ),
    ]

    events = [event async for event in agent.run(ctx, history)]

    assert len(events) == 1
    assert events[0].to_text() == "tool:bye"
    assert history.get_messages()[-1].to_text() == "tool:bye"


# --------------------------------------------------
# post_run
# --------------------------------------------------


async def test_post_run(agent: BaseAgent, ctx: AgentContext, history: History) -> None:
    events = [event async for event in agent.post_run(ctx, history)]

    assert len(events) == 1
    assert events[0].to_text() == "post_run"
    assert history.events == []
