from typing import TypeAlias

from .pre_hook_name import PreHookName

PreHookSpecifier: TypeAlias = PreHookName | str
"""
A string in the form of "{PreHookName}?{ConfigString}"

Examples:
- "confirm"
- "confirm?message=Proceed"
"""
