import logging
import os
from datetime import datetime

import yaml

from kiarina.agi.base.request_logger import BaseRequestLogger, RequestLogEntry
from kiarina.agi.base.run_context import RunContext
from kiarina.utils.app import user_directory
from kiarina.utils.file.asyncio import write_text

logger = logging.getLogger(__name__)


class LocalRequestLogger(BaseRequestLogger):
    """
    Write request logs to the local file system.
    """

    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None:
        await self._log(
            log_entry,
            phase="completed",
            run_context=run_context,
        )

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,
        *,
        run_context: RunContext,
    ) -> None:
        await self._log(
            log_entry,
            phase="failed",
            run_context=run_context,
        )

    async def _log(
        self,
        log_entry: RequestLogEntry,
        *,
        phase: str,
        run_context: RunContext,
    ) -> None:
        kind = log_entry.kind
        source = log_entry.source
        content = log_entry.content
        metadata = log_entry.metadata
        created_at = log_entry.created_at

        # Generate file path
        now = datetime.now(run_context.zone_info)

        file_path = os.path.join(
            user_directory.get_user_cache_dir(),
            "logs",
            f"{now.year:04d}",
            f"{now.month:02d}",
            f"{now.day:02d}",
            f"{now.hour:02d}{now.minute:02d}{now.second:02d}{now.microsecond:06d}-request-{kind}-{source}-{phase}.md",
        )

        # Prepare markdown content
        markdown = content

        if metadata:
            frontmatter = yaml.dump(
                {
                    "kind": kind,
                    "source": source,
                    **metadata,
                    "created_at": created_at.isoformat(),
                },
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )

            markdown = f"---\n{frontmatter}---\n\n{content}"

        # If there was an error, append its information
        await write_text(file_path, markdown)

        logger.info(f"Saved {kind} request log to {file_path}")
