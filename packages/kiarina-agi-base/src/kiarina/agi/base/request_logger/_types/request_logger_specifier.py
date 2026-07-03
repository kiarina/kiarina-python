from typing import TypeAlias

from .request_logger_name import RequestLoggerName

RequestLoggerSpecifier: TypeAlias = RequestLoggerName | str
"""
A string in the form of "{RequestLoggerName}?{ConfigString}"

Examples:
- "null"
- "null?key1=value1&key2=value2"
"""
