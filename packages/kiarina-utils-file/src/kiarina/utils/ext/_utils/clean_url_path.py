import os


def clean_url_path(file_path: str | os.PathLike[str]) -> str:
    file_path = os.path.expanduser(os.path.expandvars(os.fspath(file_path)))

    if not file_path:
        return file_path

    if "://" not in file_path:
        return file_path

    if not any(ch in file_path for ch in ("?", "#")):
        return file_path

    return file_path.split("?", 1)[0].split("#", 1)[0]
