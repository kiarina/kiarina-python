from kiarina.agi.agent._schemas.agent_context import AgentContext
from kiarina.agi.run_context import RunContext


def test_agent_context(run_context: RunContext) -> None:
    ctx = AgentContext.create(run_context=run_context, hello="world")
    assert ctx.run_kwargs == {"hello": "world"}
    assert not hasattr(ctx, "history")

    print("to_workflow_kwargs:", ctx.to_workflow_kwargs())
    print("to_tool_kwargs:", ctx.to_tool_kwargs())
