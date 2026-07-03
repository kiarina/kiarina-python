from typing import Any

import pytest

from kiarina.utils.encoding import is_binary


@pytest.mark.parametrize(
    "file_path, expected",
    [
        ("png/miineko_256x256_799b.png", True),
        ("csv/monthly_temperature_13row_141b.csv", False),
        ("pdf/text_only_portrait_1p_17kb.pdf", False),
        ("pdf/image_and_text_3p_1800kb.pdf", False),
    ],
)
def test_use_nkf(file_path: Any, expected: Any, assets_dir: Any) -> None:
    with open(assets_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert is_binary(raw_data, use_nkf=True) == expected


@pytest.mark.parametrize(
    "file_path, expected",
    [
        ("png/miineko_256x256_799b.png", True),
        ("csv/monthly_temperature_13row_141b.csv", False),
        ("pdf/text_only_portrait_1p_17kb.pdf", False),
        ("pdf/image_and_text_3p_1800kb.pdf", False),
    ],
)
def test_nouse_nkf(file_path: Any, expected: Any, assets_dir: Any) -> None:
    with open(assets_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert is_binary(raw_data, use_nkf=False) == expected
