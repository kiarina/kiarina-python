from typing import Literal

from pydantic import Field

from .base_file_info import BaseFileInfo


class OtherFileInfo(BaseFileInfo):
    type: Literal["other"] = Field(default="other", frozen=True)
