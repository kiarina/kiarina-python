import pytest

from kiarina.agi.file_utils import normalize_line_number


@pytest.mark.parametrize(
    "line_number, line_count, expected",
    [
        (1, 5, 1),
        (5, 5, 5),
        (0, 5, 1),
        (6, 5, 5),
        (-1, 5, 5),
        (-5, 5, 1),
    ],
)
def test_normalize_line_number(
    line_number: int, line_count: int, expected: int
) -> None:
    assert normalize_line_number(line_number, line_count) == expected
