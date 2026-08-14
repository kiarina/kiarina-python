import pytest
from pydantic import ValidationError

from kiarina.lib.firebase_rtdb import RTDBQuery


def test_empty() -> None:
    assert RTDBQuery().to_params() == {}


def test_order_by_is_json_encoded() -> None:
    assert RTDBQuery(order_by="$key").to_params() == {"orderBy": '"$key"'}
    assert RTDBQuery(order_by="timestamp").to_params() == {"orderBy": '"timestamp"'}


def test_limits_are_plain_integers() -> None:
    params = RTDBQuery(order_by="$key", limit_to_last=3).to_params()
    assert params == {"orderBy": '"$key"', "limitToLast": "3"}


def test_range_values_are_json_encoded() -> None:
    params = RTDBQuery(
        order_by="$key", start_after="01ABC", end_before="01XYZ"
    ).to_params()
    assert params == {
        "orderBy": '"$key"',
        "startAfter": '"01ABC"',
        "endBefore": '"01XYZ"',
    }


def test_equal_to_keeps_json_types() -> None:
    assert RTDBQuery(order_by="read", equal_to=False).to_params()["equalTo"] == "false"
    assert RTDBQuery(order_by="count", equal_to=3).to_params()["equalTo"] == "3"


def test_shallow_is_exclusive() -> None:
    assert RTDBQuery(shallow=True).to_params() == {"shallow": "true"}

    with pytest.raises(ValidationError, match="shallow cannot be combined"):
        RTDBQuery(shallow=True, order_by="$key")


def test_order_by_is_required_for_filters() -> None:
    with pytest.raises(ValidationError, match="order_by is required"):
        RTDBQuery(limit_to_last=3)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit_to_first": 1, "limit_to_last": 1},
        {"start_at": "a", "start_after": "a"},
        {"end_at": "a", "end_before": "a"},
    ],
)
def test_mutually_exclusive_pairs(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="mutually exclusive"):
        RTDBQuery(order_by="$key", **kwargs)  # type: ignore[arg-type]


def test_equal_to_cannot_be_combined_with_ranges() -> None:
    with pytest.raises(ValidationError, match="equal_to cannot be combined"):
        RTDBQuery(order_by="$key", equal_to="a", limit_to_last=1)
