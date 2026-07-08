from typing import TypeAlias

from .audio_source_name import AudioSourceName

AudioSourceSpecifier: TypeAlias = AudioSourceName | str
"""
A string in one of the following formats:

- {AudioSourceName}
- {AudioSourceName}?{ConfigString}

Examples:
- "mic"
- "mic?max_queue_size=10"
"""
