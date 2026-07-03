import os
import zipfile
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file import get_file_blob
from kiarina.agi.file_bundle import (
    FileBundle,
    FileBundleContentVisibility,
)
from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob
from kiarina.utils.mime import MIMEBlob

from .._models.langchain_media_converter import LangChainMediaConverter


@dataclass
class Result:
    text: str | None = None
    media_dicts: list[dict[str, Any]] | None = None

    def to_tuple(self) -> tuple[str | None, list[dict[str, Any]] | None]:
        return self.text, self.media_dicts


async def from_file_info(
    file_info: FileInfo,
    *,
    tag: str | None = None,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> Result:
    if file_info.metadata_only:
        return Result(text=file_info.to_metadata_only_xml(tag))

    elif file_info.type == "other":
        return Result(text=file_info.to_metadata_only_xml(tag))

    elif file_info.type == "text":
        if file_info.content_only:
            return Result(text=file_info.raw_text or "")
        else:
            return Result(text=file_info.to_xml(tag))

    elif file_info.type in ["image", "audio", "video", "pdf"]:
        if file_info.asset_uri:
            asset_blob = await get_file_blob(
                file_info.asset_uri, run_context=run_context
            )

            if not asset_blob:
                return Result()

            if _is_file_bundle(asset_blob):
                return _from_file_bundle(
                    file_info,
                    asset_blob,
                    tag,
                    capabilities,
                    media_converter,
                )

            if capabilities.is_supported(file_info.type):
                return _from_media_blob(file_info, asset_blob, tag, media_converter)

            return Result(text=file_info.to_metadata_only_xml(tag))

        else:
            if not capabilities.is_supported(file_info.type):
                return Result(text=file_info.to_metadata_only_xml(tag))

            file_blob = await get_file_blob(
                file_info.uri_or_file_path, run_context=run_context
            )

            if not file_blob:
                return Result()

            return _from_media_blob(file_info, file_blob, tag, media_converter)

    else:  # pragma: no cover
        raise AssertionError(f"Unsupported file type: {file_info.type}")


def _from_media_blob(
    file_info: FileInfo,
    file_blob: FileBlob,
    tag: str | None,
    media_converter: LangChainMediaConverter,
) -> Result:
    text: str | None = None
    media_dicts: list[dict[str, Any]] = []

    if not file_info.content_only:
        text = file_info.to_metadata_only_xml(tag)

    if file_info.type == "image":
        media_dict = media_converter.to_image_content(file_blob.mime_blob)
    elif file_info.type == "audio":
        media_dict = media_converter.to_audio_content(file_blob.mime_blob)
    elif file_info.type == "video":
        media_dict = media_converter.to_video_content(file_blob.mime_blob)
    elif file_info.type == "pdf":
        media_dict = media_converter.to_pdf_content(
            file_blob.mime_blob,
            display_name=file_info.name or os.path.basename(file_info.uri_or_file_path),
        )
    else:  # pragma: no cover
        raise AssertionError(f"Unsupported file type: {file_info.type}")

    if media_dict:
        media_dicts.append(media_dict)

    return Result(text=text, media_dicts=media_dicts or None)


def _from_file_bundle(
    file_info: FileInfo,
    file_blob: FileBlob,
    tag: str | None,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
) -> Result:
    text: str | None = None
    media_dicts: list[dict[str, Any]] = []

    parent_supported = capabilities.is_supported(file_info.type)
    bundle = FileBundle.from_bytes(file_blob.raw_data)

    for content in bundle.manifest.contents:
        if not _is_visible(content.visibility, parent_supported):
            continue

        if content.type == "text":
            media_dicts.append({"type": "text", "text": content.text})
            continue

        if not capabilities.is_supported(content.type):
            continue

        mime_blob = MIMEBlob(
            mime_type=content.mime_type,
            raw_data=bundle.files[content.file_path],
        )

        if content.type == "image":
            media_dict = media_converter.to_image_content(mime_blob)
        elif content.type == "audio":
            media_dict = media_converter.to_audio_content(mime_blob)
        elif content.type == "video":
            media_dict = media_converter.to_video_content(mime_blob)
        elif content.type == "pdf":
            media_dict = media_converter.to_pdf_content(
                mime_blob,
                display_name=os.path.basename(content.file_path),
            )
        else:  # pragma: no cover
            raise AssertionError(f"Unsupported content type in bundle: {content.type}")

        if media_dict:
            media_dicts.append(media_dict)

    if not media_dicts:
        text = file_info.to_metadata_only_xml(tag)
    elif not file_info.content_only:
        text = file_info.to_xml(tag)

    return Result(text=text, media_dicts=media_dicts or None)


def _is_file_bundle(file_blob: FileBlob) -> bool:
    if file_blob.mime_type == FileBundle.MIME_TYPE:
        return True

    return zipfile.is_zipfile(BytesIO(file_blob.raw_data))


def _is_visible(
    visibility: FileBundleContentVisibility, parent_supported: bool
) -> bool:
    if visibility == "always":
        return True
    elif visibility == "supported":
        return parent_supported
    elif visibility == "unsupported":
        return not parent_supported
    else:  # pragma: no cover
        raise AssertionError(f"Unsupported visibility: {visibility}")
