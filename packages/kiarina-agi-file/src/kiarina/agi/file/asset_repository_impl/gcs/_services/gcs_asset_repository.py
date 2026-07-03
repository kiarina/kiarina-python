import asyncio
import logging
from datetime import timedelta
from urllib.parse import urlparse

import google.cloud.exceptions
from google.cloud.storage import Blob, Client  # type: ignore

from kiarina.agi.file.asset_repository import BaseAssetRepository
from kiarina.lib.google import get_credentials
from kiarina.utils.mime import MIMEBlob, detect_mime_type

from .._settings import GCSAssetRepositorySettings

logger = logging.getLogger(__name__)


class GCSAssetRepository(BaseAssetRepository):
    def __init__(
        self,
        settings: GCSAssetRepositorySettings,
    ) -> None:
        super().__init__()
        self.settings: GCSAssetRepositorySettings = settings
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        if self._client is None:
            credentials = get_credentials(self.settings.google_auth_settings_key)
            self._client = Client(credentials=credentials)

        return self._client

    async def _exists(self, uri: str) -> bool:
        blob = self._get_blob(uri)
        return await asyncio.to_thread(blob.exists)

    async def _get(self, uri: str) -> MIMEBlob | None:
        blob = self._get_blob(uri)

        try:
            raw_data = await asyncio.to_thread(blob.download_as_bytes)
        except google.cloud.exceptions.NotFound:
            return None

        mime_type = detect_mime_type(
            file_name_hint=uri,
            raw_data=raw_data,
            default="application/octet-stream",
        )

        return MIMEBlob(mime_type=mime_type, raw_data=raw_data)

    async def _set(self, uri: str, mime_type: str, raw_data: bytes) -> None:
        blob = self._get_blob(uri)
        await asyncio.to_thread(
            blob.upload_from_string, raw_data, content_type=mime_type
        )

    async def _delete(self, uri: str) -> None:
        blob = self._get_blob(uri)

        try:
            await asyncio.to_thread(blob.delete)
        except google.cloud.exceptions.NotFound:
            pass

    async def _generate_download_url(self, uri: str, *, expire_seconds: int) -> str:
        blob = self._get_blob(uri)
        return await asyncio.to_thread(
            blob.generate_signed_url,
            expiration=timedelta(seconds=expire_seconds),
        )

    def _get_blob(self, uri: str) -> Blob:
        parsed = urlparse(uri)

        if parsed.scheme != "gs":
            raise ValueError(f"Invalid GCS URI format: {uri}")

        bucket_name = parsed.netloc
        blob_name = parsed.path.lstrip("/")

        bucket = self.client.bucket(bucket_name)
        return bucket.blob(blob_name)
