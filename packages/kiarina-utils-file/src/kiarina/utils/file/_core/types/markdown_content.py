import re
from typing import Any, NamedTuple

import yaml


class MarkdownContent(NamedTuple):
    """Markdown content and YAML front matter."""

    content: str

    metadata: dict[str, Any]

    @classmethod
    def from_text(cls, text: str) -> "MarkdownContent":
        front_matter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

        match = front_matter_pattern.match(text)

        if match:
            front_matter_text = match.group(1)
            content = text[match.end() :]

            try:
                metadata = yaml.safe_load(front_matter_text)

                if not isinstance(metadata, dict):
                    return cls(content=text, metadata={})

                if not all(isinstance(key, str) for key in metadata.keys()):
                    return cls(content=text, metadata={})

            except yaml.YAMLError:
                return cls(content=text, metadata={})
        else:
            content = text
            metadata = {}

        return cls(content=content, metadata=metadata)
