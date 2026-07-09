from typing import TypeAlias

from kiarina.agi.content import Content

from .content_spec import ContentSpec

ContentInput: TypeAlias = str | ContentSpec | Content
