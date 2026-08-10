from typing import Any

import yaml

from kiarina.agi.asset_repository import AssetArea
from kiarina.agi.file_info_builder import BuildResult
from kiarina.agi.local_repository import LocalArea
from kiarina.agi.run_context import RunContext

from .._types.storage_type import StorageType
from .create_file import create_file


async def create_markdown_file(
    file_name: str,
    *,
    content: str,
    metadata: dict[str, Any],
    sub_dir: str = "log",
    area: LocalArea | AssetArea = "data",
    storage: StorageType | None = None,
    file_info_spec_overrides: dict[str, Any] | None = None,
    run_context: RunContext,
) -> BuildResult:
    raw_text = content

    if metadata:
        yaml_frontmatter = yaml.dump(
            metadata,
            allow_unicode=True,
            sort_keys=False,
        )

        raw_text = f"---\n{yaml_frontmatter}---\n\n{content}"

    return await create_file(
        file_name,
        mime_type="text/markdown",
        raw_text=raw_text,
        sub_dir=sub_dir,
        area=area,
        storage=storage,
        file_info_spec_overrides=file_info_spec_overrides,
        run_context=run_context,
    )
