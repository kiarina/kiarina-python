def section_header(
    title: str,
    *,
    width: int = 80,
    fill_char: str = "-",
) -> str:
    x = (width - (len(title) + 2)) // 2
    y = (width - (len(title) + 2)) % 2
    return f"{fill_char * x} {title} {fill_char * (x + y)}"
