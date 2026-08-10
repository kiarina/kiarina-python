import base64
from typing import Any

from .parse_timestamp import parse_timestamp


def decode_value(value: dict[str, Any]) -> Any:
    if "nullValue" in value:
        return None

    if "booleanValue" in value:
        return value["booleanValue"]

    if "integerValue" in value:
        return int(value["integerValue"])

    if "doubleValue" in value:
        return float(value["doubleValue"])

    if "timestampValue" in value:
        return parse_timestamp(value["timestampValue"])

    if "stringValue" in value:
        return value["stringValue"]

    if "bytesValue" in value:
        return base64.b64decode(value["bytesValue"])

    if "referenceValue" in value:
        return value["referenceValue"]

    if "geoPointValue" in value:
        return value["geoPointValue"]

    if "arrayValue" in value:
        return [decode_value(item) for item in value["arrayValue"].get("values", [])]

    if "mapValue" in value:
        return {
            key: decode_value(item)
            for key, item in value["mapValue"].get("fields", {}).items()
        }

    raise ValueError(f"Unsupported Firestore value: {value}")
