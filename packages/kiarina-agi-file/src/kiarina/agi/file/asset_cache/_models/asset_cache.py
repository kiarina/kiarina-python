import hashlib
import os
import pathlib
import shutil
import time
from typing import cast

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.base.run_context import RunContext
from kiarina.agi.file.local_repository import LocalRepository, create_local_repository
from kiarina.utils.ext import detect_extension
from kiarina.utils.file import FileBlob
from kiarina.utils.mime import MIMEBlob

from .._settings import AssetCacheSettings


class AssetCache:
    def __init__(
        self,
        settings: AssetCacheSettings,
        *,
        run_context: RunContext,
    ) -> None:
        self.settings: AssetCacheSettings = settings
        self.run_context: RunContext = run_context

    @property
    def local_repository(self) -> LocalRepository:
        return create_local_repository(self.run_context)

    async def get(self, uri: str) -> FileBlob | None:
        metadata = await kfa.read_json_dict(self._get_metadata_path(uri))

        if not metadata:
            return None

        if time.time() - metadata["timestamp"] > self.settings.cache_ttl:
            await self.delete(uri)
            return None

        extension = detect_extension(metadata["mime_type"])

        if not extension:
            return None

        return await kfa.read_file(self._get_raw_data_path(uri, extension))

    async def set(
        self,
        uri: str,
        mime_type: str,
        raw_data: bytes,
    ) -> FileBlob:
        await kfa.write_json_dict(
            self._get_metadata_path(uri),
            {
                "uri": uri,
                "mime_type": mime_type,
                "timestamp": time.time(),
            },
        )

        mime_blob = MIMEBlob(mime_type, raw_data)

        file_blob = FileBlob(
            self._get_raw_data_path(uri, mime_blob.ext),
            mime_blob,
        )

        await kfa.write_file(file_blob)
        return file_blob

    async def delete(self, uri: str) -> None:
        cache_dir = self._get_cache_dir(uri)

        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

    def _get_cache_dir(self, uri: str) -> str:
        return self.local_repository.generate_cache_path(
            pathlib.Path("asset") / "cache" / self._generate_hash_string(uri)
        )

    def _get_metadata_path(self, uri: str) -> str:
        return os.path.join(self._get_cache_dir(uri), "metadata.json")

    def _get_raw_data_path(self, uri: str, extension: str) -> str:
        return os.path.join(self._get_cache_dir(uri), f"raw_data{extension}")

    def _generate_hash_string(self, uri: str) -> str:
        hash_algorithm = self.settings.hash_algorithm

        if (h := getattr(hashlib, hash_algorithm, None)) is None:  # pragma: no cover
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

        return cast(str, h(uri.encode("utf-8")).hexdigest())
