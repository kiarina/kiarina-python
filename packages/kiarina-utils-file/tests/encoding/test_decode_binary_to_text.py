import shutil

import pytest

from kiarina.utils.encoding import decode_binary_to_text


# fmt: off
@pytest.mark.skipif(shutil.which("nkf") is None, reason="nkf command not found")
@pytest.mark.parametrize(
    "raw_data, expected_text",
    [
        pytest.param("こんにちは世界".encode(), "こんにちは世界", id="utf-8"),
        pytest.param("こんにちは世界".encode('shift_jis'), "こんにちは世界", id="shift_jis"),
        pytest.param("こんにちは世界".encode('euc-jp'), "こんにちは世界", id="euc-jp"),
        pytest.param("Hello ASCII".encode('ascii'), "Hello ASCII", id="ascii"),
        pytest.param(b"", "", id="empty"),
        pytest.param("こんにちは世界🌍️".encode(), "こんにちは世界🌍️", id="utf-8-emoji"),
    ]
)
# fmt: on
def test_main(raw_data, expected_text):
    assert decode_binary_to_text(raw_data, use_nkf=True) == expected_text


@pytest.mark.parametrize(
    "file_path, expected_text",
    [
        ("png/miineko_256x256_799b.png", None),
    ],
)
def test_with_file(file_path, expected_text, assets_dir):
    with open(assets_dir / file_path, "rb") as f:
        raw_data = f.read()

    if expected_text is None:
        print(decode_binary_to_text(raw_data)[:10])
        assert True, "No exception means success"
    else:
        assert decode_binary_to_text(raw_data) == expected_text
