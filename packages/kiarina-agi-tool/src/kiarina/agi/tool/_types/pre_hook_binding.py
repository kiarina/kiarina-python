from typing import TypedDict

from kiarina.agi.pre_hook import PreHook, PreHookName
from kiarina.agi.tool_info import ToolName


class PreHookBinding(TypedDict, total=False):
    hook: PreHook | PreHookName
    apply_to: list[ToolName] | None
