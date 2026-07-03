import logging
import os
import re
from datetime import datetime

from kiarina.agi.base.run_context import RunContext
from kiarina.agi.file.asset_cache import AssetCache, create_asset_cache
from kiarina.utils.mime import MIMEBlob

from .._schemas.uri_policy import URIPolicy
from .._types.asset_area import AssetArea
from .._types.asset_repository import AssetRepository
from .._types.cached_file_blob import CachedFileBlob

logger = logging.getLogger(__name__)


class BaseAssetRepository(AssetRepository):
    def __init__(self) -> None:
        self._uri_policy: URIPolicy | None = None
        self._run_context: RunContext | None = None

    @property
    def uri_policy(self) -> URIPolicy:
        if self._uri_policy is None:
            raise ValueError("uri_policy is not configured.")

        return self._uri_policy

    @uri_policy.setter
    def uri_policy(self, uri_policy: URIPolicy) -> None:
        self._uri_policy = uri_policy

    @property
    def run_context(self) -> RunContext:
        if self._run_context is None:
            raise ValueError("run_context is not configured.")

        return self._run_context

    @run_context.setter
    def run_context(self, run_context: RunContext) -> None:
        self._run_context = run_context

    @property
    def template_variables(self) -> dict[str, str]:
        return {
            "organization_id": self.run_context.organization_id,
            "user_id": self.run_context.user_id,
            "agent_id": self.run_context.agent_id,
        }

    @property
    def asset_cache(self) -> AssetCache:
        return create_asset_cache(self.run_context)

    @property
    def data_uri(self) -> str:
        return self.uri_policy.data_dir_uri_template.format(**self.template_variables)

    @property
    def cache_uri(self) -> str:
        return self.uri_policy.cache_dir_uri_template.format(**self.template_variables)

    # --------------------------------------------------
    # Methods (File URI)
    # --------------------------------------------------

    def generate_data_uri(self, relative_path: str) -> str:
        return os.path.join(self.data_uri, relative_path)

    def generate_cache_uri(self, relative_path: str) -> str:
        return os.path.join(self.cache_uri, relative_path)

    def generate_time_based_uri(
        self,
        file_name: str | None = None,
        *,
        sub_dir_path: str = "log",
        area: AssetArea = "data",
    ) -> str:
        now = datetime.now(self.run_context.zone_info)

        relative_path = os.path.join(
            sub_dir_path,
            f"{now:%Y}",
            f"{now:%m}",
            f"{now:%d}",
            f"{now:%H%M%S}{now.microsecond:06d}",
        )

        if file_name:
            relative_path = os.path.join(relative_path, file_name)

        if area == "data":
            return self.generate_data_uri(relative_path)
        elif area == "cache":
            return self.generate_cache_uri(relative_path)
        else:  # pragma: no cover
            raise AssertionError("Invalid area value")

    def is_valid_uri(self, uri: str) -> bool:
        if not self.uri_policy.allowed_uri_patterns:
            raise ValueError("No allowed URI patterns are configured")

        for pattern in self.uri_policy.allowed_uri_patterns:
            uri_pattern = pattern.format(**self.template_variables)

            try:
                if re.match(f"^{uri_pattern}$", uri):
                    return True

            except re.error as e:
                logger.error(f"Invalid regex pattern: {uri_pattern}, error: {e!s}")
                continue

        return False

    def validate_uri(self, uri: str) -> None:
        if not self.is_valid_uri(uri):
            raise PermissionError(f"Access to the asset is not allowed: {uri}")

    # --------------------------------------------------
    # Methods (File Access)
    # --------------------------------------------------

    async def exists(self, uri: str) -> bool:
        self.validate_uri(uri)
        return await self._exists(uri)

    async def get(
        self, uri: str, *, ignore_cache: bool = False
    ) -> CachedFileBlob | None:
        self.validate_uri(uri)

        if not ignore_cache:
            if file_blob := await self.asset_cache.get(uri):
                return file_blob

        mime_blob = await self._get(uri)

        if not mime_blob:
            return None

        file_blob = await self.asset_cache.set(
            uri, mime_blob.mime_type, mime_blob.raw_data
        )

        return file_blob

    async def set(
        self,
        uri: str,
        mime_type: str,
        raw_data: bytes,
        *,
        only_not_exists: bool = False,
    ) -> CachedFileBlob:
        self.validate_uri(uri)

        if only_not_exists and await self.exists(uri):
            if file_blob := await self.asset_cache.get(uri):
                return file_blob

            return await self.asset_cache.set(uri, mime_type, raw_data)

        file_blob = await self.asset_cache.set(uri, mime_type, raw_data)

        await self._set(uri, mime_type, raw_data)

        return file_blob

    async def delete(self, uri: str) -> None:
        self.validate_uri(uri)
        await self._delete(uri)
        await self.asset_cache.delete(uri)

    async def generate_download_url(
        self,
        uri: str,
        *,
        expire_seconds: int = 86400,
    ) -> str:
        self.validate_uri(uri)
        return await self._generate_download_url(uri, expire_seconds=expire_seconds)

    # --------------------------------------------------
    # Template Methods
    # --------------------------------------------------

    async def _exists(self, uri: str) -> bool:
        raise NotImplementedError("override me")

    async def _get(self, uri: str) -> MIMEBlob | None:
        raise NotImplementedError("override me")

    async def _set(self, uri: str, mime_type: str, raw_data: bytes) -> None:
        raise NotImplementedError("override me")

    async def _delete(self, uri: str) -> None:
        raise NotImplementedError("override me")

    async def _generate_download_url(self, uri: str, *, expire_seconds: int) -> str:
        raise NotImplementedError("override me")
