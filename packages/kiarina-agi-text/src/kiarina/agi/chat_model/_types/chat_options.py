from typing import TypedDict

from kiarina.agi.tool_info import ToolChoice

from .._models.chat_model import ChatModel
from .chat_model_specifier import ChatModelSpecifier


class ChatOptions(TypedDict, total=False):
    chat_model: ChatModel | ChatModelSpecifier | None
    tool_choice: ToolChoice | None
    parallel_tool_calls: bool | None
    streaming: bool | None
