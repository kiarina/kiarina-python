from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.base.file_utils import format_xml_attributes
from kiarina.agi.base.token_utils import calc_text_token
from kiarina.agi.data.chat_estimates import ChatEstimates
from kiarina.agi.data.file_info import FileInfo, FileType


class Content(BaseModel):
    payload: dict[str, Any] | None = None

    text: str = ""
    files: list[FileInfo] = Field(default_factory=list)
    cache_control: dict[str, Any] | None = None
    tag: str = "files"
    description: str = ""
    template: str = "<{tag}{attributes}>\n{inner_xml}\n</{tag}>"
    file_tags: dict[FileType, str] = Field(default_factory=dict)

    @property
    def xml_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {}

        if self.description:
            attrs["description"] = self.description

        return attrs

    def to_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()

        if self.text:
            estimates.add_token_count("text", calc_text_token(self.text))

        if self.files:
            estimates = sum(
                [file_info.to_estimates() for file_info in self.files],
                estimates,
            )

        return estimates

    def to_xml(self, inner_xml: str | None = None) -> str:
        if not self.files:
            return ""

        if inner_xml is None:
            inner_xml = "".join(
                [
                    file_info.to_xml(
                        file_info.get_value("tag", self.file_tags.get(file_info.type))
                    )
                    for file_info in self.files
                ]
            )

        return self.template.format(
            tag=self.tag,
            attributes=format_xml_attributes(self.xml_attributes),
            inner_xml=inner_xml,
        )

    def to_text(self) -> str:
        if not self.text and not self.files:
            return ""

        if not self.files:
            return self.text

        return f"{self.to_xml()}\n\n{self.text.strip()}".strip()
