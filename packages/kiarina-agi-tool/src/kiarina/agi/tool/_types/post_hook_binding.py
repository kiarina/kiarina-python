from typing import TypedDict

from kiarina.agi.post_hook import PostHook, PostHookName
from kiarina.agi.tool_info import ToolName


class PostHookBinding(TypedDict, total=False):
    hook: PostHook | PostHookName
    apply_to: list[ToolName] | None
