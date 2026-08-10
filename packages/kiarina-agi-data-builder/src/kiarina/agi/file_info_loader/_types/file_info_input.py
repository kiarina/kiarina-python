from typing import TypeAlias

from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_builder import FileInfoSpec, FileInfoSpecifier

FileInfoInput: TypeAlias = FileInfo | FileInfoSpec | FileInfoSpecifier
