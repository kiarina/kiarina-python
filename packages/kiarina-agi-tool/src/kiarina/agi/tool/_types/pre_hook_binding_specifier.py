from typing import TypeAlias

from kiarina.agi.pre_hook import PreHookSpecifier

PreHookBindingSpecifier: TypeAlias = PreHookSpecifier | str
"""
A string in the form of "{PreHookSpecifier}@{ToolName1},{ToolName2},..."

Examples:
- "confirm"
- "confirm?message=Proceed"
- "confirm@run,finish"
- "confirm?message=Proceed@run,finish"
"""
