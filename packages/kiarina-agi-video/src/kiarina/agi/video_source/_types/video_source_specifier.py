from typing import TypeAlias

from .video_source_name import VideoSourceName

VideoSourceSpecifier: TypeAlias = VideoSourceName | str
"""
A string in one of the following formats:

- {VideoSourceName}
- {VideoSourceName}?{ConfigString}

Examples:
- "camera"
- "camera?width=640&height=480"
"""
