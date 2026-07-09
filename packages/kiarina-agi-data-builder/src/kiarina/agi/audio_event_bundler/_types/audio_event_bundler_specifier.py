from typing import TypeAlias

from .audio_event_bundler_name import AudioEventBundlerName

AudioEventBundlerSpecifier: TypeAlias = AudioEventBundlerName | str
"""
A string in one of the following formats:

- {AudioEventBundlerName}
- {AudioEventBundlerName}?{ConfigString}

Examples:
- "stt"
- "ambient?change_similarity_threshold=0.6"
"""
