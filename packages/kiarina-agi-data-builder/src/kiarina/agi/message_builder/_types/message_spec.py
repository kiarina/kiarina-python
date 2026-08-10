from typing import TypeAlias

from .ai_message_spec import AIMessageSpec
from .human_message_spec import HumanMessageSpec
from .tool_message_spec import ToolMessageSpec

MessageSpec: TypeAlias = HumanMessageSpec | AIMessageSpec | ToolMessageSpec
