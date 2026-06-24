from typing import TypeAlias

ComponentSpecifier: TypeAlias = str
"""A string in one of the following formats:

- {ComponentName}
- {ComponentName}?{ConfigString}
- {ComponentAlias}
- {ComponentAlias}?{ConfigString}

Examples:
- my_component
- my_component?key1=value1&key2=value2
"""
