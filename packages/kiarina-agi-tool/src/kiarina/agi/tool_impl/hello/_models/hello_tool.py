from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import HelloToolI18n
from .._schemas.hello_tool_schema import HelloToolSchema


@tool(tool_schema=HelloToolSchema)
def HelloTool(ctx: ToolContext) -> str:
    t = get_i18n(HelloToolI18n, ctx.run_context.language)
    return t.hello_completed
