from collections.abc import AsyncIterator, Sequence
from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext

from .._schemas.post_hook_context import PostHookContext
from .._services.post_hook_registry import post_hook_registry
from .._types.post_hook import PostHook
from .._types.post_hook_name import PostHookName


async def run_post_hooks(
    tool_call: ToolCall,
    events: list[Event],
    hooks: Sequence[PostHook | PostHookName],
    *,
    history: History | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    ctx = PostHookContext.create(
        tool_call=tool_call,
        events=events,
        history=history,
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    )

    for hook in reversed(hooks):
        if not isinstance(hook, PostHook):
            hook = post_hook_registry.resolve(hook)

        async for event in hook.run(ctx):
            yield event
