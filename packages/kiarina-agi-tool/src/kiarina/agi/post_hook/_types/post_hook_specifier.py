from typing import TypeAlias

from .post_hook_name import PostHookName

PostHookSpecifier: TypeAlias = PostHookName | str
"""
A string in the form of "{PostHookName}?{ConfigString}"

Examples:
- "notify"
- "notify?channel=dev"
"""
