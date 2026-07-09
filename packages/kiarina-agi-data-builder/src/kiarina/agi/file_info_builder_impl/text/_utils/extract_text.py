from kiarina.agi.file_utils import normalize_line_number


def extract_text(
    raw_text: str,
    *,
    start_line: int = 1,
    end_line: int = -1,
) -> str:
    lines = raw_text.split("\n")
    line_count = len(lines)
    start_line = normalize_line_number(start_line, line_count)
    end_line = normalize_line_number(end_line, line_count)
    return "\n".join(lines[start_line - 1 : end_line])
