from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.content import Content
from kiarina.agi.event import Event
from kiarina.agi.file_info import FileInfo, Group, UniqueKey, shrink_file_infos
from kiarina.agi.message import AIMessage, HumanMessage, Message
from kiarina.agi.section import BaseSection
from kiarina.agi.token_utils import TokenCount, calc_text_token
from kiarina.i18n import get_i18n

from .._i18n import FileInfoSectionI18n


class FileInfoSection(BaseSection):
    def __init__(
        self,
        *,
        group: Group | None = None,
        no_group: bool = False,
        no_unique_key: bool = False,
        ignore_unique_keys: list[UniqueKey] | None = None,
        in_message: bool | None = None,
        human_text: str | None = None,
        human_content_properties: dict[str, Any] | None = None,
        ai_text: str | None = None,
    ) -> None:
        super().__init__()

        self.group: Group | None = group
        self.no_group: bool = no_group
        self.no_unique_key: bool = no_unique_key
        self.ignore_unique_keys: list[UniqueKey] | None = ignore_unique_keys
        self.in_message: bool | None = in_message
        self.human_text: str | None = human_text
        self.human_content_properties: dict[str, Any] = human_content_properties or {}
        self.ai_text: str | None = ai_text

        self.file_infos: list[FileInfo] = []

    async def prepare(self) -> AsyncIterator[Event]:
        self.file_infos = self.ctx.history.get_file_infos(
            group=self.group,
            no_group=self.no_group,
            no_unique_key=self.no_unique_key,
            ignore_unique_keys=self.ignore_unique_keys,
            in_message=self.in_message,
        )

        if False:  # pragma: no cover
            yield

    def get_messages(self) -> list[Message]:
        if not self.file_infos:
            return []

        t = get_i18n(FileInfoSectionI18n, self.ctx.run_context.language)

        self.file_infos.sort(key=lambda fi: fi.created_at)

        return [
            HumanMessage(
                contents=[
                    Content(
                        text=self.human_text or t.human_text,
                        files=self.file_infos,
                        **self.human_content_properties,
                    )
                ]
            ),
            AIMessage(
                contents=[
                    Content(
                        text=self.ai_text or t.ai_text,
                        cache_control={"type": "ephemeral"},
                    )
                ],
            ),
        ]

    def is_resizable(self) -> bool:
        return len(self.file_infos) > 0

    async def resize(self, reduce: TokenCount) -> AsyncIterator[Event]:
        reduced = 0

        self.file_infos.sort(key=lambda fi: fi.token_count, reverse=True)

        if self.file_infos:
            self.file_infos, new_reduced = shrink_file_infos(
                self.file_infos,
                reduce=reduce,
            )
            reduced += new_reduced

        if reduced < reduce and self.file_infos:
            reduced += self._remove_file_infos(reduce - reduced)

        if False:  # pragma: no cover
            yield

    def _remove_file_infos(self, reduce: TokenCount) -> TokenCount:
        assert len(self.file_infos) > 0

        reduced = 0

        while self.file_infos and reduced < reduce:
            file_info = self.file_infos.pop(0)
            reduced += calc_text_token(file_info.to_metadata_only_xml())

        return reduced

    def _to_string(self) -> str:
        props: list[str] = []

        if self.group:
            props.append(f"g:{self.group}")

        if self.no_group:
            props.append("ng")

        if self.no_unique_key:
            props.append("nuk")

        if self.ignore_unique_keys:
            props.append(f"iuk:{','.join(self.ignore_unique_keys)}")

        if self.in_message:
            props.append("im")

        suffix = f"{{{','.join(props)}}}" if props else ""

        return f"{super()._to_string()}{suffix}"
