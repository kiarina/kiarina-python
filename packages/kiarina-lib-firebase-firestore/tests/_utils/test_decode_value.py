from datetime import datetime, timezone

import pytest

from kiarina.lib.firebase_firestore._utils.decode_value import decode_value


def test_scalar_values() -> None:
    assert decode_value({"nullValue": None}) is None
    assert decode_value({"booleanValue": True}) is True
    assert decode_value({"integerValue": "42"}) == 42
    assert decode_value({"doubleValue": 3.5}) == 3.5
    assert decode_value({"stringValue": "hello"}) == "hello"
    assert decode_value({"bytesValue": "aGVsbG8="}) == b"hello"
    assert (
        decode_value({"referenceValue": "projects/p/databases/(default)/documents/a/b"})
        == "projects/p/databases/(default)/documents/a/b"
    )
    assert decode_value({"geoPointValue": {"latitude": 35.0, "longitude": 139.0}}) == {
        "latitude": 35.0,
        "longitude": 139.0,
    }


def test_timestamp_value() -> None:
    decoded = decode_value({"timestampValue": "2026-07-28T12:34:56.123456789Z"})
    assert decoded == datetime(2026, 7, 28, 12, 34, 56, 123456, tzinfo=timezone.utc)

    decoded = decode_value({"timestampValue": "2026-07-28T12:34:56Z"})
    assert decoded == datetime(2026, 7, 28, 12, 34, 56, tzinfo=timezone.utc)


def test_array_value() -> None:
    decoded = decode_value(
        {"arrayValue": {"values": [{"integerValue": "1"}, {"stringValue": "two"}]}}
    )
    assert decoded == [1, "two"]

    assert decode_value({"arrayValue": {}}) == []


def test_map_value() -> None:
    decoded = decode_value(
        {
            "mapValue": {
                "fields": {
                    "nested": {"mapValue": {"fields": {"key": {"stringValue": "v"}}}},
                    "count": {"integerValue": "7"},
                }
            }
        }
    )
    assert decoded == {"nested": {"key": "v"}, "count": 7}

    assert decode_value({"mapValue": {}}) == {}


def test_unsupported_value() -> None:
    with pytest.raises(ValueError, match="Unsupported Firestore value"):
        decode_value({"unknownValue": "x"})
