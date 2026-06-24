from typing import TypeAlias

ObjectSpecifier: TypeAlias = str
"""A string in one of the following formats:

- {ObjectName}
- {ObjectName}?{ConfigString}
- {ObjectAlias}
- {ObjectAlias}?{ConfigString}

Examples:
- my_object
- my_object?key1=value1&key2=value2
"""
