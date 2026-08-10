from typing import TypeAlias

from kiarina.agi.post_hook import PostHookSpecifier

PostHookBindingSpecifier: TypeAlias = PostHookSpecifier | str
"""
A string in the form of "{PostHookSpecifier}@{ToolName1},{ToolName2},..."

Examples:
- "notify"
- "notify?channel=dev"
- "notify@run,finish"
- "notify?channel=dev@run,finish"
"""
