from typing import TypeAlias

from .prompt_name import PromptName

PromptSpecifier: TypeAlias = PromptName | str
"""
A string in the form of "{PromptName}?{ConfigString}"

Examples:
- "vanilla"
- "vanilla?key1=value1&key2=value2"
"""
