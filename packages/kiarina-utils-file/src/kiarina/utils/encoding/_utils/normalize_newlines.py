def normalize_newlines(text: str) -> str:
    if not text:
        return text

    return text.replace("\r\n", "\n").replace("\r", "\n")
