from typing import TypeAlias

from .workflow_name import WorkflowName

WorkflowSpecifier: TypeAlias = WorkflowName | str
"""
A string in the form of "{WorkflowName}?{ConfigString}"

Examples:
- "vanilla"
- "vanilla?key1=value1&key2=value2"
"""
