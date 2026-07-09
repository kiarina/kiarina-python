from kiarina.agi.event import HumanMessageEvent
from kiarina.agi.history import History
from kiarina.agi.prompt import invoke_prompt, prompt_registry
from kiarina.agi.run_context import RunContext


async def test_structured_prompt(run_context: RunContext) -> None:
    prompt = prompt_registry.create(
        "structured",
        system_texts=["Translate the following text to Japanese."],
    )

    events = [
        event
        async for event in invoke_prompt(
            History(events=[HumanMessageEvent.create("Hello")]),
            prompt_options={"prompt": prompt},
            run_context=run_context,
        )
    ]

    assert len(events) > 0
    assert events[-1].type == "ai_message"
