from kiarina.agi.prompt import prompt
from kiarina.agi.section import SectionContext
from kiarina.agi.section_container import SectionContainer
from kiarina.agi.section_impl.file_info import FileInfoSection
from kiarina.agi.section_impl.history import HistorySection
from kiarina.agi.section_impl.static import StaticSection
from kiarina.agi.section_impl.tool import ToolSection


@prompt
def StructuredPrompt(
    ctx: SectionContext,
    system_texts: list[str] | None = None,
    ignore_unique_keys: list[str] | None = None,
) -> SectionContainer:
    return SectionContainer(
        ctx,
        sections=[
            ToolSection(),
            StaticSection(system_texts=system_texts or []),
            FileInfoSection(
                ignore_unique_keys=ignore_unique_keys,
                in_message=False,
            ),
            HistorySection(),
        ],
    )
