from copy import deepcopy

from kiarina.agi.content import Content
from kiarina.agi.event import Event, ToolMessageEvent
from kiarina.agi.message import ToolMessage

from .._schemas.tool_context import ToolContext
from .._types.tool import Tool
from .._types.tool_output import ToolOutput


def output_to_event(ctx: ToolContext, tool: Tool, output: ToolOutput) -> Event:
    if isinstance(output, Event):
        return output

    elif isinstance(output, ToolMessage):
        return ToolMessageEvent(message=output)

    elif isinstance(output, Content):
        return ToolMessageEvent(
            message=ToolMessage(
                tool_name=ctx.tool_call.name,
                tool_call_args=deepcopy(ctx.tool_call.args),
                tool_call_id=ctx.tool_call.id,
                return_direct=tool.return_direct,
                contents=[output],
            )
        )

    else:
        return ToolMessageEvent(
            message=ToolMessage(
                tool_name=ctx.tool_call.name,
                tool_call_args=deepcopy(ctx.tool_call.args),
                tool_call_id=ctx.tool_call.id,
                return_direct=tool.return_direct,
                contents=[Content(text=output)],
            )
        )
