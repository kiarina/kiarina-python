from typing import Literal, TypeAlias

SpeakerKind: TypeAlias = Literal[
    "unknown_silence",
    "unknown_overlap",
    "speaker",
]
