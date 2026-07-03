from typing import Protocol, runtime_checkable

from kiarina.agi.base.run_context import RunContext
from kiarina.agi.file.asset_cache import AssetCache

from .._schemas.uri_policy import URIPolicy
from .asset_area import AssetArea
from .cached_file_blob import CachedFileBlob


@runtime_checkable
class AssetRepository(Protocol):
    uri_policy: URIPolicy
    run_context: RunContext

    @property
    def asset_cache(self) -> AssetCache: ...

    # --------------------------------------------------
    # Methods (File URI)
    # --------------------------------------------------

    def generate_data_uri(self, relative_path: str) -> str: ...

    def generate_cache_uri(self, relative_path: str) -> str: ...

    def generate_time_based_uri(
        self,
        file_name: str | None = None,
        *,
        sub_dir_path: str = "log",
        area: AssetArea = "data",
    ) -> str: ...

    def is_valid_uri(self, uri: str) -> bool: ...

    def validate_uri(self, uri: str) -> None: ...

    # --------------------------------------------------
    # Methods (File Access)
    # --------------------------------------------------

    async def exists(self, uri: str) -> bool: ...

    async def get(
        self,
        uri: str,
        *,
        ignore_cache: bool = False,
    ) -> CachedFileBlob | None: ...

    async def set(
        self,
        uri: str,
        mime_type: str,
        raw_data: bytes,
        *,
        only_not_exists: bool = False,
    ) -> CachedFileBlob: ...

    async def delete(self, uri: str) -> None: ...

    async def generate_download_url(
        self,
        uri: str,
        *,
        expire_seconds: int = 86400,
    ) -> str: ...
