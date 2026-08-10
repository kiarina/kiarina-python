from typing import Any

from .._schemas.document_snapshot import DocumentSnapshot
from .decode_value import decode_value
from .parse_timestamp import parse_timestamp


def parse_document(data: dict[str, Any]) -> DocumentSnapshot:
    return DocumentSnapshot(
        name=data["name"],
        fields={
            key: decode_value(value) for key, value in data.get("fields", {}).items()
        },
        create_time=parse_timestamp(data["createTime"]),
        update_time=parse_timestamp(data["updateTime"]),
    )
