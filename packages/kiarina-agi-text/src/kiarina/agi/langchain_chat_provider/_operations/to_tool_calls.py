from kiarina.agi.message import ToolCall

from .._types.lc_tool_call import LCToolCall


def to_tool_calls(lc_tool_calls: list[LCToolCall]) -> list[ToolCall]:
    tool_calls: list[ToolCall] = []

    for lc_tool_call in lc_tool_calls:
        tool_calls.append(
            ToolCall(
                id=lc_tool_call.get("id") or "",
                name=lc_tool_call.get("name") or "",
                args=lc_tool_call.get("args") or {},
            )
        )

    return tool_calls
