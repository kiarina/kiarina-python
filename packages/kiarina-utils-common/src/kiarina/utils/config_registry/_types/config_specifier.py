from typing import TypeAlias

ConfigSpecifier: TypeAlias = str
"""A string in one of the following formats:

- {ConfigName}
- {ConfigName}?{ConfigString}
- {ConfigAlias}
- {ConfigAlias}?{ConfigString}

Examples:
- vanilla
- vanilla?key1=value1&key2=value2
"""
