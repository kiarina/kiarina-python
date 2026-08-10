from collections.abc import Sequence
from typing import TypedDict

from kiarina.agi.post_hook import PostHook
from kiarina.agi.pre_hook import PreHook

from .post_hook_binding import PostHookBinding
from .post_hook_binding_specifier import PostHookBindingSpecifier
from .pre_hook_binding import PreHookBinding
from .pre_hook_binding_specifier import PreHookBindingSpecifier
from .tool import Tool
from .tool_specifier import ToolSpecifier


class ToolOptions(TypedDict, total=False):
    tools: Sequence[Tool | ToolSpecifier] | None
    pre_hooks: Sequence[PreHook | PreHookBinding | PreHookBindingSpecifier] | None
    post_hooks: Sequence[PostHook | PostHookBinding | PostHookBindingSpecifier] | None
