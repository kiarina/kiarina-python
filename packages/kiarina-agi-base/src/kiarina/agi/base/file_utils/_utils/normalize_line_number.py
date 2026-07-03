def normalize_line_number(line_number: int, line_count: int) -> int:
    if line_number < 0:
        normalized = line_count + line_number + 1
    else:
        normalized = line_number

    normalized = max(1, min(normalized, line_count))
    return normalized
