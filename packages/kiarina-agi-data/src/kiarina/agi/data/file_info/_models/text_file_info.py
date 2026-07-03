from typing import Any, Literal, Self

from pydantic import Field

from kiarina.agi.data.chat_estimates import ChatEstimates
from kiarina.agi.file_utils import normalize_line_number
from kiarina.agi.token_utils import TokenCount, calc_text_token

from .base_file_info import BaseFileInfo


class TextFileInfo(BaseFileInfo):
    type: Literal["text"] = Field(default="text", frozen=True)
    tag: str = "text_file"
    default_template: str = "<{tag}{attributes}>{raw_text}</{tag}>"
    start_line: int = 1
    end_line: int = -1
    line_count: int
    raw_text: str | None

    @property
    def xml_attributes(self) -> dict[str, Any]:
        attrs = super().xml_attributes

        if not self.start_line == 1 or not self.end_line == -1:
            attrs["start_line"] = self.normalized_start_line
            attrs["end_line"] = self.normalized_end_line

        attrs["line_count"] = self.line_count

        return attrs

    @property
    def optional_export_fields(self) -> tuple[str, ...]:
        return (*super().optional_export_fields, "start_line", "end_line")

    @property
    def normalized_start_line(self) -> int:
        return normalize_line_number(self.start_line, self.line_count)

    @property
    def normalized_end_line(self) -> int:
        return normalize_line_number(self.end_line, self.line_count)

    @property
    def segment_line_count(self) -> int:
        return self.normalized_end_line - self.normalized_start_line + 1

    def to_content_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()
        estimates.add_token_count("text", self.token_count)
        estimates.text_file_count = 1
        return estimates

    def as_metadata_only(self) -> Self:
        return self.model_copy(
            update={"metadata_only": True, "token_count": 0, "raw_text": None}
        )

    def _shrink(self, reduce: TokenCount) -> tuple[Self, TokenCount]:
        if reduce >= self.token_count or self.token_count == 0:
            return self.as_metadata_only(), self.token_count

        target: TokenCount = self.token_count - reduce

        start_line = self.normalized_start_line
        end_line = self.normalized_end_line
        line_count = end_line - start_line + 1

        lines_per_token = line_count / self.token_count
        target_line_count = max(int(lines_per_token * target) - 1, 1)

        min_lines = 1
        max_lines = target_line_count
        best_file_info: Self | None = None

        while min_lines <= max_lines:
            mid_lines = (min_lines + max_lines) // 2
            temp_file_info = self.shrink_by_line(mid_lines)

            if temp_file_info.token_count <= target:
                best_file_info = temp_file_info
                min_lines = mid_lines + 1
            else:
                max_lines = mid_lines - 1

        if best_file_info is not None:
            result_file_info = best_file_info
        else:
            result_file_info = self.as_metadata_only()

        return result_file_info, self.token_count - result_file_info.token_count

    def shrink_by_line(self, keep_line_count: int) -> Self:
        start_line = self.normalized_start_line
        end_line = self.normalized_end_line

        if self.keep_from_end:
            new_start_line = max(end_line - keep_line_count + 1, start_line)
            new_end_line = end_line
        else:
            new_start_line = start_line
            new_end_line = min(start_line + keep_line_count - 1, end_line)

        lines = (self.raw_text or "").split("\n")
        relative_start = new_start_line - start_line
        relative_end = new_end_line - start_line + 1
        new_raw_text = "\n".join(lines[relative_start:relative_end])

        return self.model_copy(
            update={
                "start_line": new_start_line,
                "end_line": new_end_line,
                "raw_text": new_raw_text,
                "token_count": calc_text_token(new_raw_text),
            }
        )
