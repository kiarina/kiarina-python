import pytest

from kiarina.utils.encoding._operations.detect_with_charset_normalizer import (
    detect_with_charset_normalizer,
)


# fmt: off
@pytest.mark.parametrize(
    "raw_data, expected_encoding",
    [
        ("こんにちは世界".encode('utf-8'), "utf-8"),
        ("Hello ASCII".encode('ascii'), "ascii"),
        (b"", None),
        ("こんにちは世界🌍️".encode('utf-8'), "utf-8"),
    ]
)
# fmt: on
def test_main(raw_data, expected_encoding):
    assert detect_with_charset_normalizer(raw_data) == expected_encoding


# Record charset_normalizer misdetections as expected failures
# fmt: off
@pytest.mark.parametrize(
    "raw_data, expected_encoding, actual_encoding",
    [
        ("こんにちは世界".encode('shift_jis'), "shift_jis", "cp932"),  # misdetected as cp932
        ("こんにちは世界".encode('euc-jp'), "euc-jp", "big5"),  # misdetected as big5
    ]
)
# fmt: on
@pytest.mark.xfail(reason="Known charset_normalizer misdetection cases")
def test_known_misdetections(raw_data, expected_encoding, actual_encoding):
    # Expected failure: charset_normalizer does not return the correct encoding
    assert detect_with_charset_normalizer(raw_data) == expected_encoding


# fmt: off
@pytest.mark.parametrize(
    "file_path, expected_encoding",
    [
        ("small/miineko_256x256_799b.png", None),
        ("large/shape_animation_1600x900_24fps_13s_4400kb.mp4", None),
        ("large/image_and_text_3p_1800kb.pdf", None),
        ("large/utf-8_1027line_125kb.txt", "utf-8"),
        ("large/ascii_code_docs_1600kb.txt", "ascii"),
    ],
)
# fmt: on
def test_with_file(file_path, expected_encoding, data_dir):
    with open(data_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert detect_with_charset_normalizer(raw_data) == expected_encoding
