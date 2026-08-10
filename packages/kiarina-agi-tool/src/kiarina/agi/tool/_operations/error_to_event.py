import asyncio
from copy import deepcopy

from kiarina.agi.content import Content
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolMessage

from .._exceptions.tool_error import ToolError
from .._schemas.tool_context import ToolContext
from .._types.tool import Tool


def error_to_event(ctx: ToolContext, tool: Tool, e: BaseException) -> ToolMessageEvent:
    if isinstance(e, asyncio.CancelledError):
        prefix = "Tool execution was cancelled by the user."
    else:
        prefix = "Tool execution failed."

    if isinstance(e, ToolError):
        suffix = str(e)
    elif isinstance(e, asyncio.CancelledError):
        suffix = ""
    else:
        suffix = f"{type(e).__name__}: {e}"

    text = f"{prefix}\n\n{ctx.tool_call.to_text()}\n\n{suffix}"

    return ToolMessageEvent(
        message=ToolMessage(
            tool_name=ctx.tool_call.name,
            tool_call_args=deepcopy(ctx.tool_call.args),
            tool_call_id=ctx.tool_call.id,
            return_direct=tool.return_direct,
            failed=True,
            contents=[Content(text=text)],
        )
    )
