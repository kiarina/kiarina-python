from typing import Any

import pytest

from kiarina.utils.encoding._operations.detect_with_charset_normalizer import (
    detect_with_charset_normalizer,
)


@pytest.mark.parametrize(
    "raw_data, expected_encoding",
    [
        ("こんにちは世界".encode(), "utf-8"),
        ("Hello ASCII".encode("ascii"), "ascii"),
        (b"", None),
        ("こんにちは世界🌍️".encode(), "utf-8"),
    ],
)
def test_main(raw_data: Any, expected_encoding: Any) -> None:
    assert detect_with_charset_normalizer(raw_data) == expected_encoding


# Record charset_normalizer misdetections as expected failures
@pytest.mark.parametrize(
    "raw_data, expected_encoding, actual_encoding",
    [
        (
            "こんにちは世界".encode("shift_jis"),
            "shift_jis",
            "cp932",
        ),  # misdetected as cp932
        ("こんにちは世界".encode("euc-jp"), "euc-jp", "big5"),  # misdetected as big5
    ],
)
@pytest.mark.xfail(reason="Known charset_normalizer misdetection cases")
def test_known_misdetections(
    raw_data: Any, expected_encoding: Any, actual_encoding: Any
) -> None:
    # Expected failure: charset_normalizer does not return the correct encoding
    assert detect_with_charset_normalizer(raw_data) == expected_encoding


@pytest.mark.parametrize(
    "file_path, expected_encoding",
    [
        ("png/miineko_256x256_799b.png", None),
        ("mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", None),
        ("pdf/image_and_text_3p_1800kb.pdf", None),
        ("txt/utf-8_1027line_125kb.txt", "utf-8"),
        ("txt/ascii_code_docs_1600kb.txt", "ascii"),
    ],
)
def test_with_file(file_path: Any, expected_encoding: Any, assets_dir: Any) -> None:
    with open(assets_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert detect_with_charset_normalizer(raw_data) == expected_encoding
