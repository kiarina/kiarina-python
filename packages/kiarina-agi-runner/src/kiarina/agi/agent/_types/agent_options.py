from typing import TypedDict

from kiarina.agi.chat_limits import ChatLimits, ChatLimitsSpecifier
from kiarina.agi.tool_info import ToolName

from .agent import Agent
from .agent_specifier import AgentSpecifier


class AgentOptions(TypedDict, total=False):
    agent: Agent | AgentSpecifier | None
    file_limits: ChatLimits | ChatLimitsSpecifier | None
    max_iterations: int
    until_end: bool
    until_tool_calls: list[ToolName]
    until_tool_runs: list[ToolName]
