import hashlib
import os
import tempfile
import urllib.request
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path
from typing import BinaryIO


def download_file(url: str, sha256: str, cache_path: os.PathLike[str] | str) -> Path:
    path = Path(cache_path)

    if path.is_file():
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = _create_temp_path(path)

    try:
        _download(url, temp_path)
        _verify_sha256(temp_path, sha256)
        os.replace(temp_path, path)
    except Exception as exc:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Failed to download file from {url} to {path}: {exc}"
        ) from exc

    return path


def _create_temp_path(path: Path) -> Path:
    descriptor, name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    os.close(descriptor)
    return Path(name)


def _download(url: str, path: Path) -> None:
    response = urllib.request.urlopen(url, timeout=60)
    with closing(response), open(path, "wb") as file:
        for chunk in _read_chunks(response):
            file.write(chunk)


def _read_chunks(response: BinaryIO) -> Iterator[bytes]:
    while chunk := response.read(1024 * 1024):
        yield chunk


def _verify_sha256(path: Path, expected: str) -> None:
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    actual = digest.hexdigest()

    if actual != expected:
        raise RuntimeError(
            f"SHA-256 mismatch for {path}: expected {expected}, got {actual}"
        )
