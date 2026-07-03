from typing import Any

import pytest

pytest.importorskip("puremagic")

from kiarina.utils.mime._operations.detect_with_puremagic import detect_with_puremagic


@pytest.mark.parametrize(
    "raw_data,file_name_hint,expected",
    [
        (b"test", "test.txt", "text/plain"),
        (b'{"key": "value"}', "config.json", "application/json"),
        (b"<html></html>", "index.html", "text/html"),
        (b"\x89PNG\r\n\x1a\n", "image.png", "image/png"),
        (b"unknown", "unknown.unknownext", None),
    ],
)
def test_with_hint(raw_data: Any, file_name_hint: Any, expected: Any) -> None:
    assert (
        detect_with_puremagic(raw_data=raw_data, file_name_hint=file_name_hint)
        == expected
    )


@pytest.mark.parametrize(
    "raw_data,expected",
    [
        (b"test", None),
        (b'{"key": "value"}', "application/json"),
        (b"<html></html>", "text/html"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (b"unknown", None),
    ],
)
def test_no_hint(raw_data: Any, expected: Any) -> None:
    assert detect_with_puremagic(raw_data=raw_data) == expected


@pytest.mark.parametrize(
    "file_path,expected",
    [
        (
            "csv/monthly_temperature_13row_141b.csv",
            None,
        ),  # CSV not detected by puremagic
        ("jpg/apple_1024x1024_138kb.jpg", "image/jpeg"),
        ("json/user_list_5row_1kb.json", None),  # JSON not detected by puremagic
        ("html/simple_160b.html", "text/html"),
        ("pdf/text_only_portrait_1p_17kb.pdf", "application/pdf"),
        ("txt/hello_world_11b.txt", None),  # only `hello world` in the file
        ("mp3/tone_2s_16kb.mp3", "audio/mpeg"),
        ("mp4/shape_animation_1600x900_24fps_13s_4400kb.mp4", "video/mp4"),
    ],
)
def test_with_file(file_path: Any, expected: Any, assets_dir: Any) -> None:
    with open(assets_dir / file_path, "rb") as f:
        raw_data = f.read()

    assert detect_with_puremagic(raw_data=raw_data) == expected
