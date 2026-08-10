from kiarina.agi.file_info_builder_impl.text._utils.extract_text import (
    extract_text,
)


def test_extract_text() -> None:
    raw_text = """Line 1
Line 2
Line 3
Line 4
Line 5
"""
    assert extract_text(raw_text, start_line=1, end_line=3) == "Line 1\nLine 2\nLine 3"
    assert extract_text(raw_text, start_line=2, end_line=4) == "Line 2\nLine 3\nLine 4"
    assert extract_text(raw_text, start_line=-3, end_line=-1) == "Line 4\nLine 5\n"
    assert (
        extract_text(raw_text, start_line=3, end_line=-1) == "Line 3\nLine 4\nLine 5\n"
    )
    assert (
        extract_text(raw_text, start_line=1, end_line=-2)
        == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    )
    assert extract_text(raw_text, start_line=-6, end_line=-1) == raw_text
    assert extract_text(raw_text, start_line=10, end_line=15) == ""
    assert extract_text(raw_text, start_line=-10, end_line=-6) == "Line 1"
    assert extract_text(raw_text, start_line=3, end_line=3) == "Line 3"
