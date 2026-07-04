from collections.abc import Iterator

import pytest

from kiarina.agi import asset_repository, local_repository
from kiarina.agi.file import get_file_blob
from kiarina.agi.run_context import RunContext
from kiarina.utils.mime import MIMEBlob


class MyAssetRepository(asset_repository.BaseAssetRepository):
    async def _get(self, uri: str) -> MIMEBlob | None:
        return None


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    asset_repository.settings_manager.cli_args = {
        "default": "my",
        "customs": {"my": f"{__name__}:MyAssetRepository"},
        "uri_policy": {
            "allowed_uri_patterns": ["my://.*"],
        },
    }
    yield
    asset_repository.settings_manager.cli_args = {}


async def test_asset(run_context: RunContext) -> None:
    file_blob = await get_file_blob("my://hello", run_context=run_context)
    assert file_blob is None


async def test_local(run_context: RunContext) -> None:
    repo = local_repository.create_local_repository(run_context)
    file_path = repo.generate_time_based_file_path("hello.txt")
    file_blob = await get_file_blob(file_path, run_context=run_context)
    assert file_blob is None
