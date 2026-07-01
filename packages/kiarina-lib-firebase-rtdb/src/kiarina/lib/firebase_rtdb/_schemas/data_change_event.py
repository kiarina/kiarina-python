from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class DataChangeEvent:
    """A data change received from Firebase Realtime Database."""

    event_type: Literal["put", "patch"]
    path: str
    data: Any
