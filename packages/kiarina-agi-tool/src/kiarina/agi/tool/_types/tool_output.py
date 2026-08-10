from typing import TypeAlias

from kiarina.agi.content import Content
from kiarina.agi.event import Event
from kiarina.agi.message import ToolMessage

ToolOutput: TypeAlias = str | Content | ToolMessage | Event
