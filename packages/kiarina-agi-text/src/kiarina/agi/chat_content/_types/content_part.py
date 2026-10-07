from typing import Any, TypeAlias

ContentPart: TypeAlias = dict[str, Any]
"""A provider-specific content block, such as `{"type": "text", "text": "..."}`."""
