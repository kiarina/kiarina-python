import pytest
from pydantic import ValidationError

from kiarina.agi.file_bundle import (
    FileBundleManifest,
    FileBundleMediaContent,
    FileBundleTextContent,
)

# --------------------------------------------------
# model_dump / model_validate
# --------------------------------------------------


def test_empty_manifest_model_dump() -> None:
    manifest = FileBundleManifest()
    assert manifest.model_dump() == {"contents": []}


def test_model_dump_with_mixed_contents() -> None:
    manifest = FileBundleManifest(
        contents=[
            FileBundleMediaContent(
                type="audio",
                file_path="audio.mp3",
                mime_type="audio/mpeg",
                visibility="supported",
            ),
            FileBundleTextContent(text="hello", visibility="unsupported"),
        ]
    )

    assert manifest.model_dump() == {
        "contents": [
            {
                "type": "audio",
                "file_path": "audio.mp3",
                "mime_type": "audio/mpeg",
                "visibility": "supported",
            },
            {
                "type": "text",
                "text": "hello",
                "visibility": "unsupported",
            },
        ]
    }


def test_model_validate_with_mixed_contents() -> None:
    manifest = FileBundleManifest.model_validate(
        {
            "contents": [
                {
                    "type": "audio",
                    "file_path": "audio.mp3",
                    "mime_type": "audio/mpeg",
                },
                {"type": "text", "text": "hello"},
            ]
        }
    )

    assert len(manifest.contents) == 2
    assert isinstance(manifest.contents[0], FileBundleMediaContent)
    assert manifest.contents[0].type == "audio"
    assert isinstance(manifest.contents[1], FileBundleTextContent)
    assert manifest.contents[1].text == "hello"


def test_model_validate_missing_contents_key_defaults_to_empty() -> None:
    manifest = FileBundleManifest.model_validate({})
    assert manifest.contents == []


def test_rejects_non_list_contents() -> None:
    with pytest.raises(ValidationError):
        FileBundleManifest.model_validate({"contents": "not a list"})


def test_rejects_non_dict_item() -> None:
    with pytest.raises(ValidationError):
        FileBundleManifest.model_validate({"contents": ["bare string"]})


def test_rejects_unknown_type_discriminator() -> None:
    with pytest.raises(ValidationError):
        FileBundleManifest.model_validate({"contents": [{"type": "unknown"}]})


def test_roundtrip() -> None:
    original = FileBundleManifest(
        contents=[
            FileBundleMediaContent(
                type="image",
                file_path="img.png",
                mime_type="image/png",
            ),
            FileBundleTextContent(text="caption"),
        ]
    )

    restored = FileBundleManifest.model_validate(original.model_dump())
    assert restored == original


# --------------------------------------------------
# create()
# --------------------------------------------------


def test_create_with_string_becomes_text_content() -> None:
    manifest = FileBundleManifest.create(["plain text"])

    assert len(manifest.contents) == 1
    content = manifest.contents[0]
    assert isinstance(content, FileBundleTextContent)
    assert content.text == "plain text"
    assert content.visibility == "always"


def test_create_with_dict_becomes_media_content() -> None:
    manifest = FileBundleManifest.create(
        [
            {
                "type": "audio",
                "file_path": "audio.mp3",
                "mime_type": "audio/mpeg",
            }
        ]
    )

    assert len(manifest.contents) == 1
    content = manifest.contents[0]
    assert isinstance(content, FileBundleMediaContent)
    assert content.type == "audio"
    assert content.file_path == "audio.mp3"


def test_create_passes_through_content_instances() -> None:
    existing_text = FileBundleTextContent(text="hi", visibility="supported")
    existing_media = FileBundleMediaContent(
        type="image",
        file_path="img.png",
        mime_type="image/png",
    )

    manifest = FileBundleManifest.create([existing_text, existing_media])
    assert manifest.contents == [existing_text, existing_media]


def test_create_with_mixed_inputs() -> None:
    manifest = FileBundleManifest.create(
        [
            "plain text",
            {"type": "video", "file_path": "v.mp4", "mime_type": "video/mp4"},
            FileBundleTextContent(text="explicit", visibility="unsupported"),
        ]
    )

    assert len(manifest.contents) == 3
    assert isinstance(manifest.contents[0], FileBundleTextContent)
    assert isinstance(manifest.contents[1], FileBundleMediaContent)
    assert isinstance(manifest.contents[2], FileBundleTextContent)
    assert manifest.contents[2].visibility == "unsupported"
