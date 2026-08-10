import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

from kiarina.agi.file import FilePath


def scan_directory(
    dir_path: str | os.PathLike[str],
    *,
    include_patterns: Sequence[str] | None = None,
    exclude_patterns: Sequence[str] | None = None,
) -> list[FilePath]:
    """
    Recursively retrieve file paths under a directory.

    - Files under .git directory are always excluded
    - Files excluded by .gitignore are excluded
    - Patterns are in glob format (supports **, *, ?)
    """
    dir_path = os.path.abspath(dir_path)

    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Directory '{dir_path}' does not exist")

    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Path '{dir_path}' is not a directory")

    file_paths: list[FilePath] = []

    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=dir_path,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip():
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            file_path = os.path.join(dir_path, line.strip())
            if os.path.isfile(file_path):
                file_paths.append(file_path)
    else:
        for path in Path(dir_path).rglob("*"):
            if path.is_file():
                file_paths.append(str(path))

    file_paths = [
        path
        for path in file_paths
        if "/.git/" not in path and not path.endswith("/.git") and "/.git\\" not in path
    ]

    filtered_paths: list[FilePath] = []

    for file_path in file_paths:
        try:
            rel_path = os.path.relpath(file_path, dir_path)
        except ValueError:  # pragma: no cover
            rel_path = file_path

        path_obj = Path(rel_path)

        if exclude_patterns:
            excluded = False
            for pattern in exclude_patterns:
                if path_obj.match(pattern) or Path(file_path).name == pattern:
                    excluded = True
                    break
            if excluded:
                continue

        if include_patterns:
            included = False
            for pattern in include_patterns:
                if path_obj.match(pattern) or Path(file_path).name == pattern:
                    included = True
                    break
            if not included:
                continue

        filtered_paths.append(file_path)

    filtered_paths.sort()

    return filtered_paths
