import sys

from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import ExitToolI18n
from .._schemas.exit_tool_schema import ExitToolSchema


@tool(tool_schema=ExitToolSchema)
def ExitTool(ctx: ToolContext, message: str, code: int = 1) -> str:
    t = get_i18n(ExitToolI18n, ctx.run_context.language)

    result = t.exit_completed.format(code=code, message=message)
    print(result, file=sys.stderr)

    sys.exit(code)
