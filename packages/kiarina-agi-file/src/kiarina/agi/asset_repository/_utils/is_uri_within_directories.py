import posixpath
from pathlib import PurePosixPath
from urllib.parse import SplitResult, urlsplit


def is_uri_within_directories(uri: str, directory_uris: list[str]) -> bool:
    parsed_uri = urlsplit(uri)

    if parsed_uri.query or parsed_uri.fragment:
        return False

    for directory_uri in directory_uris:
        parsed_directory = urlsplit(directory_uri)

        if not _has_same_location(parsed_uri, parsed_directory):
            continue

        try:
            _normalized_path(parsed_uri).relative_to(_normalized_path(parsed_directory))
            return True
        except ValueError:
            continue

    return False


def _has_same_location(uri: SplitResult, directory_uri: SplitResult) -> bool:
    return (
        uri.scheme == directory_uri.scheme
        and uri.netloc == directory_uri.netloc
        and not directory_uri.query
        and not directory_uri.fragment
    )


def _normalized_path(uri: SplitResult) -> PurePosixPath:
    return PurePosixPath(posixpath.normpath(uri.path))
