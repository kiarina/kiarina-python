from typing import Literal

from pydantic import Field

from kiarina.agi.base.file_utils import is_uri

from .base_display_content import BaseDisplayContent


class FileDisplayContent(BaseDisplayContent):
    type: Literal["file"] = Field(default="file", frozen=True)
    mime_type: str = "application/octet-stream"
    uri_or_file_path: str
    display_name: str | None = None

    @property
    def uri(self) -> str:
        if is_uri(self.uri_or_file_path):
            return self.uri_or_file_path
        else:
            return f"file://{self.uri_or_file_path}"
