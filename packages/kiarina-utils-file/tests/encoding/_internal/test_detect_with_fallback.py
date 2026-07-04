from pathlib import Path

import pytest

from kiarina.utils.encoding._operations.detect_with_fallback import detect_with_fallback


@pytest.mark.parametrize(
    "raw_data, expected_encoding",
    [
        ("こんにちは世界".encode(), "utf-8"),
        ("こんにちは世界".encode("shift_jis"), "shift_jis"),
        ("こんにちは世界".encode("euc-jp"), "euc-jp"),
        ("Hello ASCII".encode("ascii"), "utf-8"),
        (b"", None),
        ("こんにちは世界🌍️".encode(), "utf-8"),
    ],
)
def test_main(raw_data: bytes, expected_encoding: str | None) -> None:
    assert detect_with_fallback(raw_data) == expected_encoding


@pytest.mark.parametrize(
    "file_path, expected_encoding",
    [
        ("png/miineko_256x256_799b.png", None),
        ("mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", None),
        ("txt/utf-8_1027line_125kb.txt", "utf-8"),
        ("txt/ascii_code_docs_1600kb.txt", "utf-8"),
    ],
)
def test_with_file(
    file_path: str, expected_encoding: str | None, assets_dir: Path
) -> None:
    with open(assets_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert detect_with_fallback(raw_data) == expected_encoding
