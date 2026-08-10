from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from .._types.cost_kind import CostKind
from .._types.cost_source import CostSource
from .._types.microdollars import Microdollars


class CostRecord(BaseModel):
    microdollars: Microdollars = 0
    kind: CostKind
    source: CostSource
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
