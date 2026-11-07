from kiarina.agi.asset_repository import create_asset_repository
from kiarina.agi.run_context import RunContext

from .get_chat_proxy_asset_uri import get_chat_proxy_asset_uri


async def find_missing_chat_proxy_files(
    sha256s: list[str], *, run_context: RunContext
) -> list[str]:
    """
    The hashes, sorted and without repeats, of the files the chat proxy lacks. The
    files it has are touched, so they are not expired before the chat request.
    """
    asset_repository = create_asset_repository(run_context)
    missing: list[str] = []

    for sha256 in sorted(set(sha256s)):
        asset_uri = get_chat_proxy_asset_uri(asset_repository, sha256)

        if await asset_repository.exists(asset_uri):
            await asset_repository.touch(asset_uri)
        else:
            missing.append(sha256)

    return missing
