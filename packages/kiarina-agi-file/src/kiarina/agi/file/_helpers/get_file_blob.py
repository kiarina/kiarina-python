from kiarina.agi.asset_repository import create_asset_repository
from kiarina.agi.file_utils import is_uri
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import FileBlob

from .._types.uri_or_file_path import URIOrFilePath


async def get_file_blob(
    uri_or_file_path: URIOrFilePath,
    *,
    run_context: RunContext,
) -> FileBlob | None:
    if is_uri(uri_or_file_path):
        return await _get_asset_file_blob(uri_or_file_path, run_context)
    else:
        return await _get_local_file_blob(uri_or_file_path, run_context)


async def _get_asset_file_blob(
    uri: str,
    run_context: RunContext,
) -> FileBlob | None:
    asset_repository = create_asset_repository(run_context)
    return await asset_repository.get(uri)


async def _get_local_file_blob(
    file_path: str,
    run_context: RunContext,
) -> FileBlob | None:
    local_repository = create_local_repository(run_context)
    return await local_repository.get(file_path)
