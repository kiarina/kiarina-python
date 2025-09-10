import shutil

import pytest

from kiarina.utils.encoding._operations.detect_with_nkf import detect_with_nkf


# fmt: off
@pytest.mark.skipif(shutil.which("nkf") is None, reason="nkf command not found")
@pytest.mark.parametrize(
    "raw_data, expected_encoding",
    [
        ("こんにちは世界".encode('utf-8'), "utf-8"),
        ("こんにちは世界".encode('shift_jis'), "shift_jis"),
        ("こんにちは世界".encode('euc-jp'), "euc-jp"),
        ("Hello ASCII".encode('ascii'), "ascii"),
        (b"", None),
        ("こんにちは世界🌍️".encode('utf-8'), "utf-8"),
    ]
)
# fmt: on
def test_main(raw_data, expected_encoding):
    assert detect_with_nkf(raw_data) == expected_encoding


# fmt: off
@pytest.mark.skipif(shutil.which("nkf") is None, reason="nkf command not found")
@pytest.mark.parametrize(
    "file_path, expected_encoding",
    [
        ("small/miineko_256x256_799b.png", None),
        ("large/shape_animation_1600x900_24fps_13s_4400kb.mp4", None),
        ("large/utf-8_1027line_125kb.txt", "utf-8"),
        ("large/ascii_code_docs_1600kb.txt", "ascii"),
    ],
)
# fmt: on
def test_with_file(file_path, expected_encoding, data_dir):
    with open(data_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert detect_with_nkf(raw_data) == expected_encoding
