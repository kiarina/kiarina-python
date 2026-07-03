import os


def resolve_file_path(file_path: str | os.PathLike[str]) -> str:
    return os.path.abspath(os.path.expanduser(os.path.expandvars(os.fspath(file_path))))
