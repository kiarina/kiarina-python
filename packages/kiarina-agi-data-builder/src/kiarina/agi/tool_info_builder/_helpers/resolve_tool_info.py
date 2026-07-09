from kiarina.agi.tool_info import ToolInfo
from kiarina.i18n import Language

from .._types.tool_info_input import ToolInfoInput
from .build_tool_info import build_tool_info


def resolve_tool_info(
    tool_info_input: ToolInfoInput,
    *,
    language: Language,
) -> ToolInfo:
    if isinstance(tool_info_input, ToolInfo):
        return tool_info_input

    return build_tool_info(tool_info_input, language=language)
