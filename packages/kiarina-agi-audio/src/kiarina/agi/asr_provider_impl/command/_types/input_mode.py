from typing import Literal, TypeAlias

InputMode: TypeAlias = Literal["file", "stdin"]
"""
How to pass audio samples to a command ASR process.

- "file": Write samples to a temporary WAV file and pass its path via placeholders.
- "stdin": Encode samples as WAV bytes and pass them to the process standard input.
"""
