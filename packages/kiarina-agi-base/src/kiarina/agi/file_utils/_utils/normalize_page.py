def normalize_page(page_number: int, page_count: int) -> int:
    if page_number < 0:
        normalized = page_count + page_number + 1
    else:
        normalized = page_number

    normalized = max(1, min(normalized, page_count))
    return normalized
