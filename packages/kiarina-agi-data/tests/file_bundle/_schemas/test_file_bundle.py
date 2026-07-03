import json
import zipfile
from io import BytesIO

import pytest
from pydantic import ValidationError

from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleManifest,
    FileBundleMediaContent,
    FileBundleTextContent,
)
from kiarina.utils.mime import MIMEBlob


@pytest.fixture
def sample_bundle() -> FileBundle:
    return FileBundle(
        manifest=FileBundleManifest(
            contents=[
                FileBundleMediaContent(
                    type="audio",
                    file_path="audio.mp3",
                    mime_type="audio/mpeg",
                    visibility="supported",
                ),
                FileBundleTextContent(
                    text="<transcript>hi</transcript>",
                    visibility="unsupported",
                ),
            ]
        ),
        files={"audio.mp3": b"\xff\xfb\x90\x44"},
    )


def test_constants() -> None:
    assert FileBundle.MIME_TYPE == "application/zip"
    assert FileBundleManifest.FILE_NAME == "manifest.json"


def test_roundtrip_bytes(sample_bundle: FileBundle) -> None:
    restored = FileBundle.from_bytes(sample_bundle.to_bytes())

    assert restored.manifest == sample_bundle.manifest
    assert restored.files == sample_bundle.files


def test_roundtrip_mime_blob(sample_bundle: FileBundle) -> None:
    blob = sample_bundle.to_mime_blob()

    assert isinstance(blob, MIMEBlob)
    assert blob.mime_type == "application/zip"

    restored = FileBundle.from_mime_blob(blob)
    assert restored.manifest == sample_bundle.manifest
    assert restored.files == sample_bundle.files


def test_empty_bundle_roundtrip() -> None:
    bundle = FileBundle()
    restored = FileBundle.from_bytes(bundle.to_bytes())

    assert restored.manifest.contents == []
    assert restored.files == {}


def test_text_only_bundle() -> None:
    bundle = FileBundle(
        manifest=FileBundleManifest(contents=[FileBundleTextContent(text="only text")])
    )

    restored = FileBundle.from_bytes(bundle.to_bytes())
    assert len(restored.manifest.contents) == 1
    assert isinstance(restored.manifest.contents[0], FileBundleTextContent)
    assert restored.files == {}


def test_to_bytes_writes_manifest_json_entry(sample_bundle: FileBundle) -> None:
    data = sample_bundle.to_bytes()

    with zipfile.ZipFile(BytesIO(data)) as zip_file:
        names = set(zip_file.namelist())
        assert "manifest.json" in names
        assert "audio.mp3" in names

        manifest_dict = json.loads(zip_file.read("manifest.json").decode("utf-8"))
        assert manifest_dict == sample_bundle.manifest.model_dump()


def test_to_bytes_rejects_missing_referenced_file() -> None:
    bundle = FileBundle(
        manifest=FileBundleManifest(
            contents=[
                FileBundleMediaContent(
                    type="audio",
                    file_path="missing.mp3",
                    mime_type="audio/mpeg",
                )
            ]
        ),
        files={},
    )

    with pytest.raises(ValueError, match="missing referenced file"):
        bundle.to_bytes()


def test_from_bytes_rejects_missing_manifest() -> None:
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr("audio.mp3", b"data")

    with pytest.raises(ValueError, match=r"missing manifest\.json"):
        FileBundle.from_bytes(buffer.getvalue())


def test_from_bytes_rejects_non_object_manifest() -> None:
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr("manifest.json", json.dumps(["not", "an", "object"]))

    with pytest.raises(ValueError, match="must contain a JSON object"):
        FileBundle.from_bytes(buffer.getvalue())


def test_from_bytes_rejects_invalid_contents() -> None:
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr(
            "manifest.json",
            json.dumps({"contents": [{"type": "unknown"}]}),
        )

    with pytest.raises(ValidationError):
        FileBundle.from_bytes(buffer.getvalue())


def test_from_bytes_rejects_missing_referenced_file() -> None:
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr(
            "manifest.json",
            json.dumps(
                {
                    "contents": [
                        {
                            "type": "audio",
                            "file_path": "audio.mp3",
                            "mime_type": "audio/mpeg",
                        }
                    ]
                }
            ),
        )

    with pytest.raises(ValueError, match="missing referenced file"):
        FileBundle.from_bytes(buffer.getvalue())


@pytest.mark.parametrize("unsafe_path", ["../evil", "/absolute/path", "dir/../escape"])
def test_from_bytes_rejects_zip_slip(unsafe_path: str) -> None:
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr(
            "manifest.json",
            json.dumps(
                {
                    "contents": [
                        {
                            "type": "audio",
                            "file_path": unsafe_path,
                            "mime_type": "audio/mpeg",
                        }
                    ]
                }
            ),
        )
        zip_file.writestr(unsafe_path, b"x")

    with pytest.raises(ValueError, match="Unsafe file_path"):
        FileBundle.from_bytes(buffer.getvalue())


# --------------------------------------------------
# create()
# --------------------------------------------------


def test_create_delegates_to_manifest() -> None:
    bundle = FileBundle.create(
        manifest_contents=[
            "plain text",
            {"type": "audio", "file_path": "a.mp3", "mime_type": "audio/mpeg"},
        ],
        files={"a.mp3": b"data"},
    )

    assert isinstance(bundle.manifest, FileBundleManifest)
    assert len(bundle.manifest.contents) == 2
    assert isinstance(bundle.manifest.contents[0], FileBundleTextContent)
    assert isinstance(bundle.manifest.contents[1], FileBundleMediaContent)
    assert bundle.files == {"a.mp3": b"data"}


def test_create_defaults_files_to_empty_dict() -> None:
    bundle = FileBundle.create(manifest_contents=[])
    assert bundle.files == {}
    assert bundle.manifest.contents == []
