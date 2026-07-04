from typing import Any

import pytest

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.content import Content
from kiarina.agi.file_info import FileInfo
from kiarina.agi.langchain_chat_provider import LangChainMediaConverter
from kiarina.agi.langchain_chat_provider._operations.from_content import (
    from_content,
)
from kiarina.agi.langchain_chat_provider._operations.from_file_info import (
    from_file_info,
)
from kiarina.utils.file import FileBlob


@pytest.fixture
def args(capabilities: Any, media_converter: Any, run_context: Any) -> Any:
    return {
        "tag": "test_tag",
        "capabilities": capabilities,
        "media_converter": media_converter,
        "run_context": run_context,
    }


@pytest.fixture
def all_enabled_args(
    all_enabled_capabilities: Any, media_converter: Any, run_context: Any
) -> Any:
    return {
        "tag": "test_tag",
        "capabilities": all_enabled_capabilities,
        "media_converter": media_converter,
        "run_context": run_context,
    }


@pytest.fixture
def bundle_blob() -> FileBlob:
    from kiarina.agi.file_bundle import (
        FileBundle,
        FileBundleMediaContent,
        FileBundleTextContent,
    )

    bundle = FileBundle.create(
        [
            FileBundleTextContent(
                text="transcript for audio fallback",
                visibility="unsupported",
            ),
            "plain string fallback",
            FileBundleMediaContent(
                type="audio",
                file_path="audio.mp3",
                mime_type="audio/mpeg",
                visibility="supported",
            ),
            FileBundleMediaContent(
                type="image",
                file_path="frames/0001.jpg",
                mime_type="image/jpeg",
            ),
        ],
        files={
            "audio.mp3": b"audio-data",
            "frames/0001.jpg": b"image-data",
        },
    )

    return FileBlob(
        "bundle.zip",
        mime_type=FileBundle.MIME_TYPE,
        raw_data=bundle.to_bytes(),
    )


async def test_metadata_only(text_file_info: Any, args: Any) -> None:
    text_file_info.metadata_only = True
    result = await from_file_info(text_file_info, **args)
    assert result.text is not None
    assert result.media_dicts is None
    print(result)


async def test_other(other_file_info: Any, args: Any) -> None:
    result = await from_file_info(other_file_info, **args)
    assert result.text is not None
    assert result.media_dicts is None
    print(result)


async def test_text(text_file_info: Any, args: Any) -> None:
    text_file_info.content_only = True
    result = await from_file_info(text_file_info, **args)
    assert result.text is not None
    assert result.media_dicts is None
    print("content_only:", result)

    text_file_info.content_only = False
    result = await from_file_info(text_file_info, **args)
    assert result.text is not None
    assert result.media_dicts is None
    print("not content_only:", result)


async def test_asset_uri_not_found(image_file_info: FileInfo, args: Any) -> None:
    image_file_info.asset_uri = "non_existent_asset_uri"
    result = await from_file_info(image_file_info, **args)
    assert result.text is None
    assert result.media_dicts is None
    print(result)


async def test_zip_bundle_when_parent_type_is_unsupported(
    audio_file_info: FileInfo,
    bundle_blob: FileBlob,
    media_converter: LangChainMediaConverter,
    run_context: Any,
    monkeypatch: Any,
) -> None:
    audio_file_info.asset_uri = "asset://bundle.zip"

    async def fake_get_file_blob(uri_or_file_path: str, *, run_context: Any) -> Any:
        assert uri_or_file_path == "asset://bundle.zip"
        return bundle_blob

    monkeypatch.setattr(
        "kiarina.agi.langchain_chat_provider._operations.from_file_info.get_file_blob",
        fake_get_file_blob,
    )

    result = await from_file_info(
        audio_file_info,
        tag="test_tag",
        capabilities=ChatCapabilities(input_enabled={"image": True, "audio": False}),
        media_converter=media_converter,
        run_context=run_context,
    )

    assert result.text == audio_file_info.to_xml("test_tag")
    assert result.media_dicts == [
        {"type": "text", "text": "transcript for audio fallback"},
        {"type": "text", "text": "plain string fallback"},
        {"type": "image", "mime_type": "image/jpeg"},
    ]


async def test_zip_bundle_extends_multiple_media_items(
    audio_file_info: FileInfo,
    bundle_blob: FileBlob,
    all_enabled_capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: Any,
    monkeypatch: Any,
) -> None:
    audio_file_info.asset_uri = "asset://bundle.zip"

    async def fake_get_file_blob(uri_or_file_path: str, *, run_context: Any) -> Any:
        return bundle_blob

    monkeypatch.setattr(
        "kiarina.agi.langchain_chat_provider._operations.from_file_info.get_file_blob",
        fake_get_file_blob,
    )

    result = await from_content(
        "human",
        Content(files=[audio_file_info], file_tags={"audio": "test_tag"}),
        capabilities=all_enabled_capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    assert result.lc_contents == [
        {
            "type": "text",
            "text": f"<files>\n{audio_file_info.to_xml('test_tag')}\n</files>",
        },
        {
            "type": "text",
            "text": "plain string fallback",
        },
        {
            "type": "audio",
            "mime_type": "audio/mpeg",
        },
        {
            "type": "image",
            "mime_type": "image/jpeg",
        },
    ]


async def test_unsupported(audio_file_info: Any, args: Any) -> None:
    result = await from_file_info(audio_file_info, **args)
    assert result.text is not None
    assert result.media_dicts is None
    print(result)


async def test_media_asset_uri(image_file_info: Any, all_enabled_args: Any) -> None:
    image_file_info.asset_uri = image_file_info.uri_or_file_path
    result = await from_file_info(image_file_info, **all_enabled_args)
    assert result.text is not None
    assert result.media_dicts is not None
    print(result)


async def test_media_not_found(image_file_info: Any, all_enabled_args: Any) -> None:
    image_file_info.asset_uri = "non_existent_asset_uri"
    result = await from_file_info(image_file_info, **all_enabled_args)
    assert result.text is None
    assert result.media_dicts is None
    print(result)


async def test_media_content_only(image_file_info: Any, all_enabled_args: Any) -> None:
    image_file_info.content_only = True
    result = await from_file_info(image_file_info, **all_enabled_args)
    assert result.text is None
    assert result.media_dicts is not None
    print("content_only:", result)


async def test_image(image_file_info: Any, all_enabled_args: Any) -> None:
    result = await from_file_info(image_file_info, **all_enabled_args)
    assert result.text is not None
    assert result.media_dicts is not None
    print(result)


async def test_audio(audio_file_info: Any, all_enabled_args: Any) -> None:
    result = await from_file_info(audio_file_info, **all_enabled_args)
    assert result.text is not None
    assert result.media_dicts is not None
    print(result)


async def test_video(video_file_info: Any, all_enabled_args: Any) -> None:
    result = await from_file_info(video_file_info, **all_enabled_args)
    assert result.text is not None
    assert result.media_dicts is not None
    print(result)


async def test_pdf(pdf_file_info: Any, all_enabled_args: Any) -> None:
    result = await from_file_info(pdf_file_info, **all_enabled_args)
    assert result.text is not None
    assert result.media_dicts is not None
    print(result)
