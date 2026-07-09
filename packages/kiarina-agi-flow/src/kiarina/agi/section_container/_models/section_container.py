import logging
from collections.abc import AsyncIterator

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.content import Content
from kiarina.agi.event import Event
from kiarina.agi.message import Message, SystemMessage
from kiarina.agi.section import Section, SectionContext, Weight
from kiarina.agi.token_utils import TokenCount
from kiarina.agi.tool_info import ToolInfo

logger = logging.getLogger(__name__)


class SectionContainer:
    def __init__(
        self,
        ctx: SectionContext,
        *,
        sections: list[Section | tuple[Section, Weight]] | None = None,
    ) -> None:
        self.ctx: SectionContext = ctx
        self.sections: list[Section] = []

        if sections:
            self.add_sections(sections)

    # ----------------------------------------
    # Methods (Section Management)
    # ----------------------------------------

    def add_sections(self, sections: list[Section | tuple[Section, Weight]]) -> None:
        for item in sections:
            if isinstance(item, tuple):
                section, weight = item
                self.add_section(section, weight)
            else:
                self.add_section(item)

    def add_section(self, section: Section, weight: Weight | None = None) -> None:
        if weight is not None:
            section.weight = weight

        self.sections.append(section)

    # ----------------------------------------
    # Methods (Prompt Generation)
    # ----------------------------------------

    async def prepare(self) -> AsyncIterator[Event]:
        for section in self.sections:
            section.ctx = self.ctx

            async for event in section.prepare():
                yield event

    def get_messages(self) -> list[Message]:
        messages: list[Message] = []

        if system_message := self._get_system_message():
            messages.append(system_message)

        for section in self.sections:
            messages.extend(section.get_messages())

        return messages

    def get_tool_infos(self) -> list[ToolInfo]:
        tool_infos: list[ToolInfo] = []

        for section in self.sections:
            tool_infos.extend(section.get_tool_infos())

        seen_names: set[str] = set()
        unique_tool_infos: list[ToolInfo] = []

        for tool_info in tool_infos:
            if tool_info.name not in seen_names:
                seen_names.add(tool_info.name)
                unique_tool_infos.append(tool_info)

        if unique_tool_infos:
            unique_tool_infos[-1].cache_control = {"type": "ephemeral"}

        return unique_tool_infos

    def get_estimates(self, ignore_cache: bool = False) -> ChatEstimates:
        estimates = ChatEstimates()

        for section in self.sections:
            estimates += section.get_estimates(ignore_cache)

        return estimates

    def is_resizable(self) -> bool:
        return any(section.is_resizable() for section in self.sections)

    async def resize(self, token_count_limit: int) -> AsyncIterator[Event]:
        resize_infos = self._calc_resize_infos(token_count_limit)

        logger.debug(
            "Resizing SectionContainer to fit within %d tokens.\n%s",
            token_count_limit,
            "\n".join(
                f"  {section.__class__.__name__}: {reduce} tokens"
                for section, reduce in resize_infos
            ),
        )

        for section, reduce in resize_infos:
            async for event in section.resize(reduce):
                yield event

    async def ready(self) -> AsyncIterator[Event]:
        for section in self.sections:
            async for event in section.ready():
                yield event

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _get_system_message(self) -> SystemMessage | None:
        texts = [
            text for section in self.sections for text in section.get_system_texts()
        ]

        if not texts:
            return None

        return SystemMessage(contents=[Content(text=text) for text in texts])

    def _calc_resize_infos(self, limit: TokenCount) -> list[tuple[Section, TokenCount]]:
        """
        Calculate the sections to resize upon overflow occurrence and the respective token amounts to resize for each section.
        """
        available: TokenCount = limit
        resizable_sections: list[Section] = []

        # Subtract the number of tokens in sections that cannot be resized
        for section in self.sections:
            if not section.is_resizable():
                available -= section.get_estimates().token_count
            else:
                resizable_sections.append(section)

        if available <= 0:
            raise ValueError(
                "Non-resizable sections alone exceed token limit."
                "Please review the structure of the section."
            )

        while True:
            # Distribute available tokens according to surplus token occupancy weight.
            # Subtract the token count of sections
            # that are not overflowing within that frame.
            # Repeat until there are no sections that are not overflowing.
            has_non_overflow_section = False

            total_weight = sum(section.weight for section in resizable_sections)

            for section in resizable_sections:
                if (
                    section.get_estimates().token_count
                    <= available * section.weight / total_weight
                ):
                    has_non_overflow_section = True
                    available -= section.get_estimates().token_count
                    resizable_sections.remove(section)
                    break

            if not has_non_overflow_section:
                break

        total_weight = sum(section.weight for section in resizable_sections)

        return [
            (
                section,
                section.get_estimates().token_count
                - int(available * section.weight / total_weight),
            )
            for section in resizable_sections
        ]

    # ----------------------------------------
    # Magic Methods
    # ----------------------------------------

    def __str__(self) -> str:
        props: list[str] = []

        for section in self.sections:
            props.append(f"{section}")

        return " ".join(props)
