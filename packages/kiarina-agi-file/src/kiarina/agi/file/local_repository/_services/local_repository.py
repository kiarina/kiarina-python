import logging
import os
import re
from datetime import datetime

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import user_directory
from kiarina.utils.file import FileBlob

from .._schemas.file_path_policy import FilePathPolicy
from .._settings import LocalRepositorySettings
from .._types.local_area import LocalArea
from .._utils.resolve_file_path import resolve_file_path

logger = logging.getLogger(__name__)


class LocalRepository:
    def __init__(self, settings: LocalRepositorySettings, *, run_context: RunContext):
        self.settings: LocalRepositorySettings = settings
        self.run_context: RunContext = run_context

    @property
    def template_variables(self) -> dict[str, str]:
        return {
            "user_data_dir": str(user_directory.get_user_data_dir()),
            "user_cache_dir": str(user_directory.get_user_cache_dir()),
            "organization_id": self.run_context.organization_id,
            "user_id": self.run_context.user_id,
            "agent_id": self.run_context.agent_id,
        }

    @property
    def file_path_policy(self) -> FilePathPolicy:
        return self.settings.file_path_policy

    @property
    def data_dir(self) -> str:
        return self.file_path_policy.data_dir_path_template.format(
            **self.template_variables
        )

    @property
    def cache_dir(self) -> str:
        return self.file_path_policy.cache_dir_path_template.format(
            **self.template_variables
        )

    # ----------------------------------------
    # Methods (File Path)
    # ----------------------------------------

    def generate_data_path(self, relative_path: str | os.PathLike[str]) -> str:
        return os.path.join(self.data_dir, os.fspath(relative_path))

    def generate_cache_path(self, relative_path: str | os.PathLike[str]) -> str:
        return os.path.join(self.cache_dir, os.fspath(relative_path))

    def generate_time_based_dir_path(
        self,
        *,
        sub_dir_path: str | os.PathLike[str] = "log",
        area: LocalArea = "data",
    ) -> str:
        now = datetime.now(self.run_context.zone_info)

        relative_path = os.path.join(
            os.fspath(sub_dir_path),
            f"{now:%Y}",
            f"{now:%m}",
            f"{now:%d}",
            f"{now:%H%M%S}{now.microsecond:06d}",
        )

        if area == "data":
            return self.generate_data_path(relative_path)
        elif area == "cache":
            return self.generate_cache_path(relative_path)
        else:  # pragma: no cover
            raise AssertionError("Invalid area value")

    def generate_time_based_file_path(
        self,
        file_name: str,
        *,
        sub_dir_path: str | os.PathLike[str] = "log",
        area: LocalArea = "data",
    ) -> str:
        dir_path = self.generate_time_based_dir_path(
            sub_dir_path=sub_dir_path, area=area
        )

        return os.path.join(dir_path, file_name)

    def is_valid_file_path(self, file_path: str | os.PathLike[str]) -> bool:
        file_path = resolve_file_path(file_path)

        for pattern in self.settings.file_path_policy.allowed_file_path_patterns:
            file_path_pattern = pattern.format(**self.template_variables)

            try:
                if re.match(f"^{file_path_pattern}$", file_path):
                    return True

            except re.error as e:
                logger.error(
                    f"Invalid regex pattern: {file_path_pattern}, error: {e!s}"
                )
                continue

        return False

    def validate_file_path(self, file_path: str | os.PathLike[str]) -> None:
        if not self.is_valid_file_path(file_path):
            raise PermissionError(
                f"Access to the file path is not allowed: {file_path}"
            )

    # ----------------------------------------
    # Methods (File Access)
    # ----------------------------------------

    async def exists(self, file_path: str | os.PathLike[str]) -> bool:
        file_path = resolve_file_path(file_path)
        self.validate_file_path(file_path)

        if not os.path.exists(file_path):
            return False

        if os.path.isdir(file_path):
            return False

        return True

    async def get(self, file_path: str | os.PathLike[str]) -> FileBlob | None:
        file_path = resolve_file_path(file_path)
        self.validate_file_path(file_path)
        return await kfa.read_file(file_path)

    async def set(
        self,
        file_path: str | os.PathLike[str],
        mime_type: str,
        raw_data: bytes,
        *,
        only_not_exists: bool = False,
    ) -> FileBlob:
        file_path = resolve_file_path(file_path)
        self.validate_file_path(file_path)

        file_blob = FileBlob(file_path, mime_type=mime_type, raw_data=raw_data)

        if only_not_exists and await self.exists(file_path):
            return file_blob

        await kfa.write_binary(file_path, raw_data)

        logger.debug(f"Saved file to local repository: {file_path}")

        return file_blob

    async def delete(self, file_path: str | os.PathLike[str]) -> None:
        file_path = resolve_file_path(file_path)
        self.validate_file_path(file_path)
        await kfa.remove_file(file_path)
