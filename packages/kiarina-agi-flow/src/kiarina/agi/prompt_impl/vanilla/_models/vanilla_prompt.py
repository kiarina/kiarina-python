from kiarina.agi.prompt import prompt
from kiarina.agi.section import SectionContext
from kiarina.agi.section_container import SectionContainer
from kiarina.agi.section_impl.file_info import FileInfoSection
from kiarina.agi.section_impl.history import HistorySection
from kiarina.agi.section_impl.tool import ToolSection


@prompt
def VanillaPrompt(ctx: SectionContext) -> SectionContainer:
    return SectionContainer(
        ctx,
        sections=[
            ToolSection(),
            FileInfoSection(
                in_message=False,
            ),
            HistorySection(),
        ],
    )
