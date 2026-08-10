from typing import Any, overload

from kiarina.agi.asset_repository import AssetArea
from kiarina.agi.asset_utils import create_asset_file
from kiarina.agi.file_info_builder import BuildResult
from kiarina.agi.local_repository import LocalArea
from kiarina.agi.local_utils import create_local_file
from kiarina.agi.run_context import RunContext
from kiarina.utils.mime import MIMEBlob

from .._settings import settings_manager
from .._types.storage_type import StorageType


@overload
async def create_file(
    file_name: str,
    mime_blob: MIMEBlob,
    *,
    sub_dir: str = "log",
    area: LocalArea | AssetArea = "data",
    storage: StorageType | None = None,
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult: ...


@overload
async def create_file(
    file_name: str,
    *,
    mime_type: str,
    raw_data: bytes,
    sub_dir: str = "log",
    area: LocalArea | AssetArea = "data",
    storage: StorageType | None = None,
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult: ...


@overload
async def create_file(
    file_name: str,
    *,
    mime_type: str,
    raw_text: str,
    sub_dir: str = "log",
    area: LocalArea | AssetArea = "data",
    storage: StorageType | None = None,
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult: ...


async def create_file(
    file_name: str,
    mime_blob: MIMEBlob | None = None,
    *,
    mime_type: str | None = None,
    raw_data: bytes | None = None,
    raw_text: str | None = None,
    sub_dir: str = "log",
    area: LocalArea | AssetArea = "data",
    storage: StorageType | None = None,
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult:
    settings = settings_manager.get_settings()

    if storage is None:
        storage = settings.storage

    if storage == "local":
        return await create_local_file(
            file_name,
            mime_blob,
            mime_type=mime_type,
            raw_data=raw_data,
            raw_text=raw_text,
            sub_dir_path=sub_dir,
            area=area,
            file_info_spec_overrides=file_info_spec_overrides,
            run_context=run_context,
        )

    elif storage == "asset":
        return await create_asset_file(
            file_name,
            mime_blob,
            mime_type=mime_type,
            raw_data=raw_data,
            raw_text=raw_text,
            sub_dir=sub_dir,
            area=area,
            file_info_spec_overrides=file_info_spec_overrides,
            run_context=run_context,
        )

    else:  # pragma: no cover
        raise AssertionError(f"Unsupported storage type: {storage}")
