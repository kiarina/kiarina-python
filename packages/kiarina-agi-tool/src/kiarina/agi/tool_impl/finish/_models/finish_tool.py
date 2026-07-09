from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import FinishToolI18n
from .._schemas.finish_tool_schema import FinishToolSchema


@tool(tool_schema=FinishToolSchema, return_direct=True)
def FinishTool(ctx: ToolContext) -> str:
    t = get_i18n(FinishToolI18n, ctx.run_context.language)
    return t.finish_completed
