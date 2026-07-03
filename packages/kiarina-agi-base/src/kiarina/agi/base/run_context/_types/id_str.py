from typing import Annotated

from pydantic import StringConstraints

_ID_PATTERN = r"^[a-zA-Z0-9._-]+$"
"""
Permitted ID patterns

Alphanumeric characters, dot, underscore, hyphen, one character or more.
"""

IDStr = Annotated[str, StringConstraints(min_length=1, pattern=_ID_PATTERN)]
"""
ID String type
"""
