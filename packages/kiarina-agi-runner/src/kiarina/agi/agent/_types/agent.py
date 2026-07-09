from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from kiarina.agi.event import Event
from kiarina.agi.history import History

from .._schemas.agent_context import AgentContext
from .agent_name import AgentName


@runtime_checkable
class Agent(Protocol):
    name: AgentName

    def pre_run(self, ctx: AgentContext, history: History) -> AsyncIterator[Event]: ...
    def run(self, ctx: AgentContext, history: History) -> AsyncIterator[Event]: ...
    def post_run(self, ctx: AgentContext, history: History) -> AsyncIterator[Event]: ...
