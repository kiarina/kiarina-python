from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.section import SectionContext
from kiarina.agi.section_impl.tool import ToolSection
from kiarina.agi.tool_info import ToolInfo


def test_tool_section(run_context: RunContext) -> None:
    section = ToolSection()
    section.ctx = SectionContext.create(
        history=History(
            tool_infos=[
                ToolInfo(name="tool3", description="third tool"),
                ToolInfo(name="tool2", description="second tool", state="inactive"),
                ToolInfo(name="tool1", description="first tool"),
                ToolInfo(name="tool0", description="zero tool"),
            ]
        ),
        run_context=run_context,
    )

    assert [tool_info.name for tool_info in section.get_tool_infos()] == [
        "tool3",
        "tool1",
        "tool0",
    ]
