import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.message import AIMessage, Message, ToolMessage
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolOptions
from kiarina.agi.workflow import WorkflowOptions

from .._exceptions.missing_tools_error import MissingToolsError
from .._schemas.agent_context import AgentContext
from .._services.agent_registry import agent_registry
from .._settings import settings_manager
from .._types.agent import Agent
from .._types.agent_options import AgentOptions

logger = logging.getLogger(__name__)


async def run_agent(
    history: History,
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    workflow_options: WorkflowOptions | None = None,
    tool_options: ToolOptions | None = None,
    agent_options: AgentOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    stop_event: asyncio.Event | None = None,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    agent_options = agent_options or {}

    agent = agent_options.get("agent")

    if not isinstance(agent, Agent):
        agent = agent_registry.resolve(agent)

    file_limits = agent_options.get("file_limits")

    if not isinstance(file_limits, ChatLimits):
        file_limits = ChatLimits.from_specifier(file_limits or "")

    max_iterations = (
        agent_options.get("max_iterations") or settings_manager.settings.max_iterations
    )

    until_end = agent_options.get("until_end") or False
    until_tool_calls = agent_options.get("until_tool_calls") or []
    until_tool_runs = agent_options.get("until_tool_runs") or []

    ctx = AgentContext.create(
        file_limits=file_limits,
        chat_options=chat_options,
        prompt_options=prompt_options,
        workflow_options=workflow_options,
        tool_options=tool_options,
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    )

    iterations = 0

    while True:
        if stop_event is not None and stop_event.is_set():
            logger.debug("Agent loop stopped by stop event")
            break

        if _is_conversation_end(history):
            break

        if _is_iteration_end(history, agent_options, iterations, max_iterations):
            break

        iterations += 1
        new_events: list[Event] = []
        ctx.run_context = run_context.with_metadata(
            loop=_format_loop(
                iterations=iterations,
                max_iterations=max_iterations,
                until_end=until_end,
                until_tool_calls=until_tool_calls,
                until_tool_runs=until_tool_runs,
            ),
            agent=str(agent),
        )

        try:
            async for event in _run_agent_iteration(ctx, history, agent):
                yield event
                new_events.append(event)

        except MissingToolsError as e:
            logger.debug(f"Missing tools called: {', '.join(e.tool_names)}")
            break

        last_message = _get_last_message_from_events(new_events)

        if last_message is None:
            break

        if isinstance(last_message, ToolMessage) and last_message.return_direct:
            break

        if until_tool_calls and isinstance(last_message, AIMessage):
            if any(
                tool_call.name in until_tool_calls
                for tool_call in last_message.tool_calls
            ):
                logger.debug("Until tool calls reached")
                break

        if until_tool_runs and isinstance(last_message, ToolMessage):
            if last_message.tool_name in until_tool_runs:
                logger.debug("Until tool runs reached")
                break


async def _run_agent_iteration(
    ctx: AgentContext,
    history: History,
    agent: Agent,
) -> AsyncIterator[Event]:
    async for event in agent.pre_run(ctx, history):
        yield event

    async for event in agent.run(ctx, history):
        yield event

    async for event in agent.post_run(ctx, history):
        yield event


def _is_conversation_end(history: History) -> bool:
    message = _get_last_message(history)
    return isinstance(message, AIMessage) and not message.tool_calls


def _is_iteration_end(
    history: History,
    agent_options: AgentOptions,
    iterations: int,
    max_iterations: int,
) -> bool:
    return iterations >= max_iterations and not _should_continue_until_end(
        history,
        agent_options,
    )


def _should_continue_until_end(
    history: History,
    agent_options: AgentOptions,
) -> bool:
    return agent_options.get("until_end", False) and _is_last_tool_call(history)


def _is_last_tool_call(history: History) -> bool:
    message = _get_last_message(history)
    return isinstance(message, AIMessage) and bool(message.tool_calls)


def _format_loop(
    *,
    iterations: int,
    max_iterations: int,
    until_end: bool,
    until_tool_calls: list[str],
    until_tool_runs: list[str],
) -> str:
    return (
        f"{iterations}/{max_iterations}"
        f"{' until_end' if until_end else ''}"
        f"{' until_tool_calls(' + ','.join(until_tool_calls) + ')' if until_tool_calls else ''}"
        f"{' until_tool_runs(' + ','.join(until_tool_runs) + ')' if until_tool_runs else ''}"
    ).strip()


def _get_last_message(history: History) -> Message | None:
    messages = history.get_messages()

    if not messages:
        return None

    return messages[-1]


def _get_last_message_from_events(events: list[Event]) -> Message | None:
    for event in reversed(events):
        if (
            event.type == "human_message"
            or event.type == "ai_message"
            or event.type == "tool_message"
        ):
            return event.message

    return None
