from typing import TypeAlias

from .audio_consumer_name import AudioConsumerName

AudioConsumerSpecifier: TypeAlias = AudioConsumerName | str
"""
A string in one of the following formats:

- {AudioConsumerName}
- {AudioConsumerName}?{ConfigString}

Examples:
- "ambient"
- "ambient?window_seconds=5.0"
"""
