from kiarina.agi.asset_repository import create_asset_repository
from kiarina.agi.run_context import RunContext

from .get_chat_proxy_asset_uri import get_chat_proxy_asset_uri


async def find_missing_chat_proxy_files(
    sha256s: list[str], *, run_context: RunContext
) -> list[str]:
    """The hashes, sorted and without repeats, of the files the chat proxy lacks."""
    asset_repository = create_asset_repository(run_context)

    return [
        sha256
        for sha256 in sorted(set(sha256s))
        if not await asset_repository.exists(
            get_chat_proxy_asset_uri(asset_repository, sha256)
        )
    ]
