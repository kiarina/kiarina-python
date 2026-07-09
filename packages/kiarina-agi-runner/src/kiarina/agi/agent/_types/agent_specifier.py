from typing import TypeAlias

from .agent_name import AgentName

AgentSpecifier: TypeAlias = AgentName | str
"""
A string in the form of "{AgentName}?{ConfigString}"

Examples:
- "vanilla"
- "vanilla?key1=value1&key2=value2"
"""
