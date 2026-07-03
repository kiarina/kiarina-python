from typing import TypeAlias

from .chat_logger_name import ChatLoggerName

ChatLoggerSpecifier: TypeAlias = ChatLoggerName | str
"""
A string in the form of "{ChatLoggerName}?{ConfigString}"

Examples:
- "null"
- "null?key1=value1&key2=value2"
"""
