from typing import TypeAlias

from .file_segment_normalizer_name import FileSegmentNormalizerName

FileSegmentNormalizerSpecifier: TypeAlias = FileSegmentNormalizerName | str
"""
A string in one of the following formats:

- {FileSegmentNormalizerName}
- {FileSegmentNormalizerName}?{ConfigString}

Examples:
- "text"
- "text?merge_adjacent=True"
"""
