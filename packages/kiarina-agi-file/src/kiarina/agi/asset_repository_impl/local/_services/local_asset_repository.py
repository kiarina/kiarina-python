from urllib.parse import urlparse

from kiarina.agi.asset_repository import BaseAssetRepository
from kiarina.agi.local_repository import LocalRepository, create_local_repository
from kiarina.utils.app import user_directory
from kiarina.utils.mime import MIMEBlob


class LocalAssetRepository(BaseAssetRepository):
    @property
    def template_variables(self) -> dict[str, str]:
        return {
            **super().template_variables,
            "user_data_dir": str(user_directory.get_user_data_dir()),
            "user_cache_dir": str(user_directory.get_user_cache_dir()),
        }

    @property
    def local_repository(self) -> LocalRepository:
        return create_local_repository(self.run_context)

    async def _exists(self, uri: str) -> bool:
        return await self.local_repository.exists(uri)

    async def _get(self, uri: str) -> MIMEBlob | None:
        if file_blob := await self.local_repository.get(uri):
            return file_blob.mime_blob

        return None

    async def _set(self, uri: str, mime_type: str, raw_data: bytes) -> None:
        await self.local_repository.set(uri, mime_type, raw_data)

    async def _delete(self, uri: str) -> None:
        await self.local_repository.delete(uri)

    async def _generate_download_url(self, uri: str, *, expire_seconds: int) -> str:
        return f"file://{urlparse(uri).path}"
