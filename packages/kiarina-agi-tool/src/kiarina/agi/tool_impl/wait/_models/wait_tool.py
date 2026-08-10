import asyncio

from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import WaitToolI18n
from .._schemas.wait_tool_schema import WaitToolSchema


@tool(tool_schema=WaitToolSchema)
async def WaitTool(ctx: ToolContext, wait_time: float) -> str:
    await asyncio.sleep(wait_time)

    t = get_i18n(WaitToolI18n, ctx.run_context.language)
    return t.wait_completed.format(wait_time=wait_time)
