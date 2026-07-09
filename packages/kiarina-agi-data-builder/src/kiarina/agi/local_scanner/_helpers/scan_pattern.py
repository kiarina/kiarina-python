import glob
from pathlib import Path

from kiarina.agi.file import FilePath

from .._schemas.local_path_spec import LocalPathSpec
from .._types.local_path_pattern import LocalPathPattern
from .._utils.scan_directory import scan_directory


def scan_pattern(local_path: LocalPathPattern | LocalPathSpec) -> list[FilePath]:
    if isinstance(local_path, str):
        local_path_spec = LocalPathSpec.from_string(local_path)
    else:
        local_path_spec = local_path

    matched_files = glob.glob(local_path_spec.expanded_path_pattern, recursive=True)

    file_paths: list[FilePath] = []
    seen: set[FilePath] = set()

    for matched_file in matched_files:
        file_path = Path(matched_file).resolve()

        if file_path.is_dir():
            dir_file_paths = scan_directory(
                str(file_path),
                include_patterns=local_path_spec.include_patterns,
                exclude_patterns=local_path_spec.exclude_patterns,
            )

            for path in dir_file_paths:
                if path not in seen:
                    file_paths.append(path)
                    seen.add(path)

        else:
            str_path = str(file_path)

            if str_path not in seen:
                file_paths.append(str_path)
                seen.add(str_path)

    file_paths.sort()

    return file_paths
