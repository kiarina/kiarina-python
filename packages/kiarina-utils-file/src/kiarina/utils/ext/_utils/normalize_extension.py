def normalize_extension(extension: str) -> str:
    extension = extension.strip().lower()

    if not extension:
        return ""

    if not extension.startswith("."):
        extension = f".{extension}"

    return extension
