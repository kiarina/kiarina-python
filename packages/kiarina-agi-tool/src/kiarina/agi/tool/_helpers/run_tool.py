import asyncio
import logging
from collections.abc import AsyncIterator, Sequence
from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.event import CustomEvent, Event
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall
from kiarina.agi.post_hook import (
    PostHook,
    post_hook_registry,
    run_post_hooks,
)
from kiarina.agi.pre_hook import (
    PreHook,
    pre_hook_registry,
    run_pre_hooks,
)
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolName
from kiarina.agi.tool_logger import tool_logger_registry

from .._exceptions.tool_not_found_error import ToolNotFoundError
from .._operations.error_to_event import error_to_event
from .._schemas.tool_context import ToolContext
from .._services.tool_registry import tool_registry
from .._types.post_hook_binding import PostHookBinding
from .._types.post_hook_binding_specifier import PostHookBindingSpecifier
from .._types.pre_hook_binding import PreHookBinding
from .._types.pre_hook_binding_specifier import PreHookBindingSpecifier
from .._types.tool import Tool
from .._types.tool_options import ToolOptions

logger = logging.getLogger(__name__)


async def run_tool(
    tool_call: ToolCall,
    *,
    history: History | None = None,
    tool_options: ToolOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    tool_options = tool_options or {}
    cost_recorder = cost_recorder or NullCostRecorder()

    tool = _get_tool(tool_call.name, tool_options.get("tools") or [])

    if not tool:
        raise ToolNotFoundError(tool_call.name)

    pre_hooks = _get_pre_hooks(tool_call.name, tool_options.get("pre_hooks") or [])
    post_hooks = _get_post_hooks(tool_call.name, tool_options.get("post_hooks") or [])

    run_context = run_context.with_metadata(tool=str(tool))

    ctx = ToolContext.create(
        tool_call=tool_call,
        history=history,
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    )

    tool_logger = tool_logger_registry.resolve()
    tool_logger.log_tool_start(tool_call, run_context)

    try:
        events: list[Event] = []

        async for event in run_pre_hooks(
            tool_call=tool_call,
            hooks=pre_hooks,
            history=history,
            cost_recorder=cost_recorder,
            run_context=run_context,
            **kwargs,
        ):
            yield event

        async for event in tool.run(ctx):
            if event.type == "tool_message":
                tool_logger.log_tool_end(event.message, run_context)

            yield event
            events.append(event)

        async for event in run_post_hooks(
            tool_call=tool_call,
            events=events,
            hooks=post_hooks,
            history=history,
            cost_recorder=cost_recorder,
            run_context=run_context,
            **kwargs,
        ):
            yield event

    except asyncio.CancelledError as e:
        logger.warning(f"Tool {tool_call} execution was cancelled")

        yield CustomEvent(
            payload={
                "type": "tool_cancelled",
                "tool_call": tool_call,
            }
        )

        event = error_to_event(ctx, tool, e)
        tool_logger.log_tool_end(event.message, run_context)
        yield event

    except Exception as e:
        logger.error(f"Tool {tool_call} was failed: {e}", exc_info=True)

        event = error_to_event(ctx, tool, e)
        tool_logger.log_tool_end(event.message, run_context)
        yield event


def _get_tool(
    tool_name: ToolName,
    tools: Sequence[Tool | ToolName],
) -> Tool | None:
    for tool in tools:
        if isinstance(tool, str):
            if tool == tool_name:
                return tool_registry.create(tool)
        elif tool.name == tool_name:
            return tool

    return None


def _get_pre_hooks(
    tool_name: ToolName,
    hook_configs: Sequence[PreHook | PreHookBinding | PreHookBindingSpecifier],
) -> list[PreHook]:
    hooks: list[PreHook] = []

    for hook_config in hook_configs:
        if isinstance(hook_config, str):
            if "@" in hook_config:
                specifier, apply_to_string = hook_config.split("@", 1)
                apply_to = apply_to_string.split(",")

                if not apply_to or tool_name in apply_to:
                    hooks.append(pre_hook_registry.resolve(specifier))
            else:
                hooks.append(pre_hook_registry.resolve(hook_config))

        elif isinstance(hook_config, dict):
            apply_to = hook_config.get("apply_to") or []

            if apply_to and tool_name not in apply_to:
                continue

            hook = hook_config.get("hook")

            if hook is None:  # pragma: no cover
                continue

            if isinstance(hook, str):
                hooks.append(pre_hook_registry.resolve(hook))
            else:
                hooks.append(hook)

        else:
            hooks.append(hook_config)

    return hooks


def _get_post_hooks(
    tool_name: ToolName,
    hook_configs: Sequence[PostHook | PostHookBinding | PostHookBindingSpecifier],
) -> list[PostHook]:
    hooks: list[PostHook] = []

    for hook_config in hook_configs:
        if isinstance(hook_config, str):
            if "@" in hook_config:
                specifier, apply_to_string = hook_config.split("@", 1)
                apply_to = apply_to_string.split(",")

                if not apply_to or tool_name in apply_to:
                    hooks.append(post_hook_registry.resolve(specifier))
            else:
                hooks.append(post_hook_registry.resolve(hook_config))

        elif isinstance(hook_config, dict):
            apply_to = hook_config.get("apply_to") or []

            if apply_to and tool_name not in apply_to:
                continue

            hook = hook_config.get("hook")

            if hook is None:  # pragma: no cover
                continue

            if isinstance(hook, str):
                hooks.append(post_hook_registry.resolve(hook))
            else:
                hooks.append(hook)

        else:
            hooks.append(hook_config)

    return hooks
