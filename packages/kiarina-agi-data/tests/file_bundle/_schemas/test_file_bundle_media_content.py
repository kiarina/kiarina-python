import pytest
from pydantic import ValidationError

from kiarina.agi.data.file_bundle import FileBundleMediaContent


def test_model_dump() -> None:
    content = FileBundleMediaContent(
        type="audio",
        file_path="audio.mp3",
        mime_type="audio/mpeg",
        visibility="supported",
    )

    assert content.model_dump() == {
        "type": "audio",
        "file_path": "audio.mp3",
        "mime_type": "audio/mpeg",
        "visibility": "supported",
    }


def test_model_validate() -> None:
    content = FileBundleMediaContent.model_validate(
        {
            "type": "image",
            "file_path": "image.png",
            "mime_type": "image/png",
            "visibility": "always",
        }
    )

    assert content.type == "image"
    assert content.file_path == "image.png"
    assert content.mime_type == "image/png"
    assert content.visibility == "always"


def test_default_visibility_is_always() -> None:
    content = FileBundleMediaContent.model_validate(
        {
            "type": "video",
            "file_path": "video.mp4",
            "mime_type": "video/mp4",
        }
    )

    assert content.visibility == "always"


@pytest.mark.parametrize("media_type", ["image", "audio", "video", "pdf"])
def test_accepts_all_media_types(media_type: str) -> None:
    content = FileBundleMediaContent.model_validate(
        {
            "type": media_type,
            "file_path": f"file.{media_type}",
            "mime_type": f"application/{media_type}",
        }
    )

    assert content.type == media_type


def test_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        FileBundleMediaContent.model_validate(
            {
                "type": "text",
                "file_path": "a.txt",
                "mime_type": "text/plain",
            }
        )

    with pytest.raises(ValidationError):
        FileBundleMediaContent.model_validate(
            {
                "type": "unknown",
                "file_path": "a.bin",
                "mime_type": "application/octet-stream",
            }
        )


def test_roundtrip() -> None:
    original = FileBundleMediaContent(
        type="pdf",
        file_path="doc.pdf",
        mime_type="application/pdf",
        visibility="unsupported",
    )

    restored = FileBundleMediaContent.model_validate(original.model_dump())
    assert restored == original
