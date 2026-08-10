from collections.abc import Sequence
from typing import TypeAlias

from kiarina.agi.event_builder import EventInput
from kiarina.agi.history import History

from .history_spec import HistorySpec

HistoryInput: TypeAlias = History | HistorySpec | Sequence[EventInput] | str
