import os

from kiarina.agi.asset_repository import AssetRepository


def get_chat_proxy_asset_uri(asset_repository: AssetRepository, sha256: str) -> str:
    """The asset URI where the chat proxy keeps the file with this hash."""
    return asset_repository.generate_cache_uri(os.path.join("chat_proxy", sha256))
