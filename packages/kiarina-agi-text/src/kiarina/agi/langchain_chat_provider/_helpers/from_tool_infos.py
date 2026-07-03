from typing import cast

from langchain_core.utils.function_calling import convert_to_openai_function

from kiarina.agi.tool_info import ToolInfo

from .._types.lc_tool_info import LCToolInfo


def from_tool_infos(tool_infos: list[ToolInfo]) -> list[LCToolInfo]:
    lc_tool_infos: list[LCToolInfo] = []

    for tool_info in tool_infos:
        lc_tool_info = cast(
            LCToolInfo, convert_to_openai_function(tool_info.to_json_schema())
        )

        if tool_info.cache_control:
            lc_tool_info["cache_control"] = tool_info.cache_control

        lc_tool_infos.append(lc_tool_info)

    return lc_tool_infos
