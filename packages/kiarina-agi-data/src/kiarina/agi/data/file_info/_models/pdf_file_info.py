from typing import Any, Literal

from pydantic import Field

from kiarina.agi.data.chat_estimates import ChatEstimates
from kiarina.agi.file_utils import normalize_page

from .base_file_info import BaseFileInfo


class PDFFileInfo(BaseFileInfo):
    type: Literal["pdf"] = Field(default="pdf", frozen=True)
    tag: str = "pdf_file"
    start_page: int = 1
    end_page: int = -1
    page_count: int

    @property
    def xml_attributes(self) -> dict[str, Any]:
        attrs = super().xml_attributes

        if not self.start_page == 1 or not self.end_page == -1:
            attrs["start_page"] = self.normalized_start_page
            attrs["end_page"] = self.normalized_end_page

        attrs["page_count"] = self.segment_page_count

        return attrs

    @property
    def optional_export_fields(self) -> tuple[str, ...]:
        return (*super().optional_export_fields, "start_page", "end_page")

    @property
    def normalized_start_page(self) -> int:
        return normalize_page(self.start_page, self.page_count)

    @property
    def normalized_end_page(self) -> int:
        return normalize_page(self.end_page, self.page_count)

    @property
    def segment_page_count(self) -> int:
        return self.normalized_end_page - self.normalized_start_page + 1

    def to_content_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()
        estimates.add_token_count("pdf", self.token_count)
        estimates.pdf_file_count = 1
        estimates.pdf_page_count = self.segment_page_count
        estimates.file_size = self.file_size
        return estimates
