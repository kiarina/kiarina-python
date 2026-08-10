import hashlib
import io
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock

import pytest

from kiarina.utils.common import download_file


def test_download_file_downloads_and_verifies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"model"
    urlopen = Mock(return_value=io.BytesIO(content))
    monkeypatch.setattr(
        "kiarina.utils.common._helpers.download_file.urllib.request.urlopen", urlopen
    )

    result = download_file(
        "https://example.com/model.onnx",
        hashlib.sha256(content).hexdigest(),
        tmp_path / "models" / "example" / "model.onnx",
    )

    assert result == tmp_path / "models" / "example" / "model.onnx"
    assert result.read_bytes() == content
    urlopen.assert_called_once_with("https://example.com/model.onnx", timeout=60)


def test_download_file_reuses_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "models" / "example" / "model.onnx"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"cached")
    urlopen = Mock()
    monkeypatch.setattr(
        "kiarina.utils.common._helpers.download_file.urllib.request.urlopen", urlopen
    )

    result = download_file(
        "https://example.com/model.onnx",
        "not-checked",
        path,
    )

    assert result == path
    urlopen.assert_not_called()


def test_download_file_removes_hash_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "kiarina.utils.common._helpers.download_file.urllib.request.urlopen",
        lambda *_args, **_kwargs: io.BytesIO(b"invalid"),
    )

    path = tmp_path / "models" / "example" / "model.onnx"

    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        download_file(
            "https://example.com/model.onnx",
            hashlib.sha256(b"expected").hexdigest(),
            path,
        )

    assert not path.exists()
    assert list(path.parent.glob("*.tmp")) == []


def test_download_file_reports_download_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*_args: object, **_kwargs: object) -> io.BytesIO:
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(
        "kiarina.utils.common._helpers.download_file.urllib.request.urlopen", fail
    )

    path = tmp_path / "models" / "example" / "model.onnx"

    with pytest.raises(
        RuntimeError,
        match=r"https://example.com/model\.onnx.*models/example",
    ):
        download_file(
            "https://example.com/model.onnx",
            "unused",
            path,
        )

    assert list(path.parent.glob("*.tmp")) == []


def test_download_file_is_atomic_during_concurrent_downloads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"model"
    monkeypatch.setattr(
        "kiarina.utils.common._helpers.download_file.urllib.request.urlopen",
        lambda *_args, **_kwargs: io.BytesIO(content),
    )

    path = tmp_path / "models" / "example" / "model.onnx"

    def download() -> Path:
        return download_file(
            "https://example.com/model.onnx",
            hashlib.sha256(content).hexdigest(),
            path,
        )

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda _: download(), range(8)))

    assert len(set(results)) == 1
    assert results[0].read_bytes() == content
    assert list(results[0].parent.glob("*.tmp")) == []
