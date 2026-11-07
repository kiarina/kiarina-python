import os
from urllib.parse import urlparse

import pytest

from kiarina.agi.asset_repository import URIPolicy
from kiarina.agi.asset_repository_impl.local import LocalAssetRepository
from kiarina.agi.run_context import RunContext


@pytest.fixture
def asset_repository(run_context: RunContext) -> LocalAssetRepository:
    repository = LocalAssetRepository()
    repository.uri_policy = URIPolicy(
        allowed_uri_patterns=[".*"],
        data_dir_uri_template="{user_data_dir}/{agent_id}/asset",
        cache_dir_uri_template="{user_cache_dir}/{agent_id}/asset",
    )
    repository.run_context = run_context
    return repository


def test_template_variables(asset_repository: LocalAssetRepository) -> None:
    print("Template Variables:", asset_repository.template_variables)


async def test_touch(asset_repository: LocalAssetRepository) -> None:
    uri = asset_repository.generate_cache_uri("test_touch.txt")
    await asset_repository.set(uri, "text/plain", b"test")
    file_path = urlparse(uri).path
    os.utime(file_path, (0, 0))

    await asset_repository.touch(uri)

    assert os.path.getmtime(file_path) > 0
