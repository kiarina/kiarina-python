from typing import TypeAlias

from .._models.file_display_content import FileDisplayContent
from .._models.text_display_content import TextDisplayContent

DisplayContent: TypeAlias = TextDisplayContent | FileDisplayContent
