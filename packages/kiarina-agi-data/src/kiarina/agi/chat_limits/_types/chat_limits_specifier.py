from typing import TypeAlias

ChatLimitsSpecifier: TypeAlias = str
"""
A string in one of the following formats:

- "{ConfigString}"
- "{JSONString}"

Format:
- ConfigString: A comma-separated list of key=value pairs.
- JSONString: A JSON string compatible with kiarina.agi.chat_limits.ChatLimits.

Examples:
- "token_count_limit=4096"
- "audio_file_count_limit=1,video_file_count_limit=1"
"""
