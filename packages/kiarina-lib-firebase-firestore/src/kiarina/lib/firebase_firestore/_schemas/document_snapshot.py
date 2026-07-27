from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class DocumentSnapshot:
    """A document retrieved from Cloud Firestore."""

    name: str
    fields: dict[str, Any]
    create_time: datetime
    update_time: datetime

    @property
    def path(self) -> str:
        return self.name.split("/documents/", 1)[1]

    @property
    def id(self) -> str:
        return self.name.rsplit("/", 1)[-1]
