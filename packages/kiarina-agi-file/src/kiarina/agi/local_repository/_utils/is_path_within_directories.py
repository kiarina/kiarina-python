import os
from pathlib import Path


def is_path_within_directories(
    file_path: str | os.PathLike[str],
    directories: list[str | os.PathLike[str]],
) -> bool:
    resolved_path = Path(file_path).resolve()

    for directory in directories:
        try:
            resolved_path.relative_to(Path(directory).resolve())
            return True
        except ValueError:
            continue

    return False
