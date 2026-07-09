from kiarina.agi.run_context import RunContext
from kiarina.agi.section import SectionContext


def test_section_context(run_context: RunContext) -> None:
    ctx = SectionContext.create(
        run_context=run_context,
        custom_arg="custom_value",
    )

    assert ctx.run_kwargs["custom_arg"] == "custom_value"
    print(ctx.to_dict())
