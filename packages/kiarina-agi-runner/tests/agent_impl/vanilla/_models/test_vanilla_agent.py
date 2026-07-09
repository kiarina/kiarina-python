from kiarina.agi.agent import BaseAgent
from kiarina.agi.agent_impl.vanilla import VanillaAgent


def test_vanilla_agent() -> None:
    agent = VanillaAgent()
    assert isinstance(agent, BaseAgent)
