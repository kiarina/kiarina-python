from typing import TypeAlias

from kiarina.agi.file import URIOrFilePath

FileInfoSpecifier: TypeAlias = URIOrFilePath | str
"""
A string in one of the following formats:

- {URIOrFilePath}
- {URIOrFilePath}?{ConfigString}
- {JSONString}

Examples:
- "/path/to/file.txt"
- "gcs://bucket_name/file.txt"
- "/path/to/file.txt?start_line=10&end_line=20"
- '{"uri_or_file_path": "/path/to/file.txt", "start_line": 10, "end_line": 20}'
"""
