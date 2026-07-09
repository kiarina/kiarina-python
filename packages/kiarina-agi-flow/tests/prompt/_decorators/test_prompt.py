from dataclasses import dataclass

from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.history import History
from kiarina.agi.prompt import prompt
from kiarina.agi.run_context import RunContext
from kiarina.agi.section import SectionContext
from kiarina.agi.section_container import SectionContainer
from kiarina.agi.section_impl.static import StaticSection


async def test_sync(run_context: RunContext) -> None:
    @prompt
    def MyPrompt(ctx: SectionContext) -> SectionContainer:
        """This is my prompt."""
        return SectionContainer(ctx)

    my_prompt = MyPrompt()

    assert MyPrompt.__name__ == "MyPrompt"
    assert MyPrompt.__doc__ == "This is my prompt."
    assert MyPrompt.__module__ == __name__
    assert hasattr(my_prompt, "get_section_container")
    assert callable(my_prompt.get_section_container)

    container = await my_prompt.get_section_container(
        history=History(),
        chat_options={},
        cost_recorder=NullCostRecorder(),
        run_context=run_context,
    )
    assert isinstance(container, SectionContainer)


async def test_async(run_context: RunContext) -> None:
    @prompt
    async def MyPrompt(ctx: SectionContext) -> SectionContainer:
        return SectionContainer(ctx)

    my_prompt = MyPrompt()

    assert MyPrompt.__name__ == "MyPrompt"
    assert hasattr(my_prompt, "get_section_container")
    assert callable(my_prompt.get_section_container)

    container = await my_prompt.get_section_container(
        history=History(),
        chat_options={},
        cost_recorder=NullCostRecorder(),
        run_context=run_context,
    )
    assert isinstance(container, SectionContainer)


async def test_init_kwargs(run_context: RunContext) -> None:
    @prompt
    def EditablePrompt(
        ctx: SectionContext,
        message: str = "hello",
    ) -> SectionContainer:
        return SectionContainer(
            ctx,
            sections=[StaticSection(system_texts=[message])],
        )

    prompt_instance = EditablePrompt()

    container_no_kwargs = await prompt_instance.get_section_container(
        history=History(),
        chat_options={},
        cost_recorder=NullCostRecorder(),
        run_context=run_context,
    )

    assert container_no_kwargs.get_messages()[0].contents[0].text == "hello"

    prompt_instance = EditablePrompt(message="custom message")

    container_with_kwargs = await prompt_instance.get_section_container(
        history=History(),
        chat_options={},
        cost_recorder=NullCostRecorder(),
        run_context=run_context,
    )

    assert container_with_kwargs.get_messages()[0].contents[0].text == "custom message"


async def test_custom_section_context(run_context: RunContext) -> None:
    @dataclass
    class MySectionContext(SectionContext):
        extra_field: str = "extra_value"

    @prompt
    def MyPrompt(ctx: SectionContext) -> SectionContainer:
        custom_context = MySectionContext(
            **ctx.to_dict(),
            extra_field="extra_value",
        )

        return SectionContainer(
            custom_context,
            sections=[StaticSection(system_texts=[custom_context.extra_field])],
        )

    my_prompt = MyPrompt()

    sc = await my_prompt.get_section_container(
        history=History(),
        chat_options={},
        cost_recorder=NullCostRecorder(),
        run_context=run_context,
    )

    messages = sc.get_messages()
    assert len(messages) == 1
    assert messages[0].contents[0].text == "extra_value"
