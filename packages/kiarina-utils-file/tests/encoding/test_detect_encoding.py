import shutil

import pytest

from kiarina.utils.encoding import detect_encoding


# fmt: off
@pytest.mark.skipif(shutil.which("nkf") is None, reason="nkf command not found")
@pytest.mark.parametrize(
    "raw_data, expected_encoding",
    [
        pytest.param("こんにちは世界".encode('utf-8'), "utf-8", id="utf-8"),
        pytest.param("こんにちは世界".encode('shift_jis'), "shift_jis", id="shift_jis"),  # Detected as cp932
        pytest.param("こんにちは世界".encode('euc-jp'), "euc-jp", id="euc-jp"),        # Detected as big5
        pytest.param("Hello ASCII".encode('ascii'), "ascii", id="ascii"),
        pytest.param(b"", None, id="empty"),
        pytest.param("こんにちは世界🌍️".encode('utf-8'), "utf-8", id="utf-8-emoji"),
    ]
)
# fmt: on
def test_main(raw_data, expected_encoding):
    assert detect_encoding(raw_data, use_nkf=True) == expected_encoding


@pytest.mark.parametrize(
    "file_path, expected_encoding",
    [
        ("small/miineko_256x256_799b.png", None),
    ],
)
def test_with_file(file_path, expected_encoding, data_dir):
    with open(data_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert detect_encoding(raw_data, use_nkf=True) == expected_encoding
