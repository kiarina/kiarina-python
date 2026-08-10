from collections.abc import Sequence
from typing import TypedDict

from kiarina.agi.event_builder import EventsInput
from kiarina.agi.file_info_loader import FileInfoInput
from kiarina.agi.tool_info import ToolInfo
from kiarina.agi.tool_info_builder import ToolInfoSpecifier


class HistorySpec(TypedDict, total=False):
    events: EventsInput | None
    file_infos: Sequence[FileInfoInput] | None
    tool_infos: Sequence[ToolInfo | ToolInfoSpecifier] | None
