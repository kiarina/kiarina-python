from typing import TypeAlias

from .file_info_builder_name import FileInfoBuilderName

FileInfoBuilderSpecifier: TypeAlias = FileInfoBuilderName | str
"""
A string in one of the following formats:

- {FileInfoBuilderName}
- {FileInfoBuilderName}?{ConfigString}
- {FileInfoBuilderAlias}
- {FileInfoBuilderAlias}?{ConfigString}

Examples:
- "text"
- "pdf?ocr=True"
"""
