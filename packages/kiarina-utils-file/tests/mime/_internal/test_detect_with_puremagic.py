import pytest

pytest.importorskip("puremagic")

from kiarina.utils.mime._operations.detect_with_puremagic import detect_with_puremagic


# fmt: off
@pytest.mark.parametrize(
    "raw_data,file_name_hint,expected",
    [
        (b"test", "test.txt", "text/plain"),
        (b"{\"key\": \"value\"}", "config.json", "application/json"),
        (b"<html></html>", "index.html", "text/html"),
        (b"\x89PNG\r\n\x1a\n", "image.png", "image/png"),
        (b"unknown", "unknown.unknownext", None),
    ],
)
# fmt: on
def test_with_hint(raw_data, file_name_hint, expected):
    assert (
        detect_with_puremagic(raw_data=raw_data, file_name_hint=file_name_hint)
        == expected
    )


# fmt: off
@pytest.mark.parametrize(
    "raw_data,expected",
    [
        (b"test", None),
        (b"{\"key\": \"value\"}", "application/json"),
        (b"<html></html>", "text/html"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (b"unknown", None),
    ],
)
# fmt: on
def test_no_hint(raw_data, expected):
    assert detect_with_puremagic(raw_data=raw_data) == expected


# fmt: off
@pytest.mark.parametrize(
    "file_path,expected",
    [
        ("small/monthly_temperature_13row_141b.csv", None),  # CSV not detected by puremagic
        ("small/apple_1024x1024_138kb.jpg", "image/jpeg"),
        ("small/user_list_5row_1kb.json", None),  # JSON not detected by puremagic
        ("small/simple_160b.html", "text/html"),
        ("small/text_only_portrait_1p_17kb.pdf", "application/pdf"),
        ("small/hello_world_11b.txt", None),  # only `hello world` in the file
        ("small/tone_2s_16kb.mp3", "audio/mpeg"),
        ("large/shape_animation_1600x900_24fps_13s_4400kb.mp4", "video/mp4"),
    ],
)
# fmt: on
def test_with_file(file_path, expected, data_dir):
    with open(data_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert detect_with_puremagic(raw_data=raw_data) == expected
