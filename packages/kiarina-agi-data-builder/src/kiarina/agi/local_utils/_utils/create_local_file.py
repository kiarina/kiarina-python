from typing import Any, cast, overload

from kiarina.agi.file_info_builder import (
    BuildResult,
    FileInfoSpec,
    build_file_info,
)
from kiarina.agi.local_repository import LocalArea, create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.utils.mime import MIMEBlob, detect_mime_type


@overload
async def create_local_file(
    file_name: str,
    mime_blob: MIMEBlob,
    *,
    sub_dir_path: str = "log",
    area: LocalArea = "data",
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult: ...


@overload
async def create_local_file(
    file_name: str,
    *,
    mime_type: str,
    raw_data: bytes,
    sub_dir_path: str = "log",
    area: LocalArea = "data",
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult: ...


@overload
async def create_local_file(
    file_name: str,
    *,
    mime_type: str,
    raw_text: str,
    sub_dir_path: str = "log",
    area: LocalArea = "data",
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult: ...


@overload
async def create_local_file(
    file_name: str,
    mime_blob: MIMEBlob | None = None,
    *,
    mime_type: str | None = None,
    raw_data: bytes | None = None,
    raw_text: str | None = None,
    sub_dir_path: str = "log",
    area: LocalArea = "data",
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult: ...


async def create_local_file(
    file_name: str,
    mime_blob: MIMEBlob | None = None,
    *,
    mime_type: str | None = None,
    raw_data: bytes | None = None,
    raw_text: str | None = None,
    sub_dir_path: str = "log",
    area: LocalArea = "data",
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult:
    mime_blob = _get_mime_blob(mime_blob, mime_type, raw_data, raw_text)

    local_repository = create_local_repository(run_context)

    file_path = local_repository.generate_time_based_file_path(
        file_name,
        sub_dir_path=sub_dir_path,
        area=area,
    )

    file_blob = await local_repository.set(
        file_path,
        mime_blob.mime_type,
        mime_blob.raw_data,
    )

    file_info_spec = cast(
        FileInfoSpec,
        {
            "uri_or_file_path": file_path,
            **(file_info_spec_overrides or {}),
        },
    )

    file = await build_file_info(file_info_spec, file_blob, run_context=run_context)

    return file


def _get_mime_blob(
    mime_blob: MIMEBlob | None = None,
    mime_type: str | None = None,
    raw_data: bytes | None = None,
    raw_text: str | None = None,
) -> MIMEBlob:
    if mime_blob:
        return mime_blob

    if not mime_type and raw_data:
        mime_type = detect_mime_type(
            raw_data=raw_data,
            default="application/octet-stream",
        )

    if not mime_type:  # pragma: no cover
        raise ValueError("mime_type or raw_data must be provided")

    if raw_data is None and raw_text is None:  # pragma: no cover
        raise ValueError("raw_data or raw_text must be provided")

    return MIMEBlob(mime_type, raw_data, raw_text=raw_text)
