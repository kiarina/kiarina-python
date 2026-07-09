from typing import TypeAlias

LocalPathPattern: TypeAlias = str
"""
A string in one of the following formats:

- {PathPattern}
- {PathPattern}?{ConfigString}

Formats:

- PathPattern: A glob pattern for local file paths, with support for ``~`` and environment variable expansion.
- ConfigString: A query string with the following optional parameters:
    - include: file patterns to include when scanning a directory (comma-separated)
    - exclude: file patterns to exclude when scanning a directory (comma-separated)

Examples:
- "~/src/myproject/**/*.py"
- "~/src/myproject?include=*.py,*.pyi&exclude=*_test.py"
"""
