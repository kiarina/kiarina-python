from typing import Any

import pytest

from kiarina.agi.asset_repository import (
    AssetRepository,
    create_asset_repository,
    settings_manager,
)


@pytest.fixture()
def setup() -> Any:
    settings_manager.cli_args = {
        "uri_policy": {
            "allowed_uri_patterns": [
                "{user_data_dir}/{agent_id}/asset/.*",
                "{user_cache_dir}/{agent_id}/asset/.*",
            ],
            "data_dir_uri_template": "{user_data_dir}/{agent_id}/asset",
            "cache_dir_uri_template": "{user_cache_dir}/{agent_id}/asset",
        },
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def asset_repository(setup: Any, run_context: Any) -> Any:
    return create_asset_repository(run_context)


def test_generate_time_based_uri(asset_repository: AssetRepository) -> None:
    uri = asset_repository.generate_time_based_uri("test.txt", area="data")
    print("Generated URI (Data):", uri)
    uri = asset_repository.generate_time_based_uri("test.txt", area="cache")
    print("Generated URI (Cache):", uri)


def test_validate_uri(asset_repository: AssetRepository) -> None:
    asset_repository.validate_uri(asset_repository.generate_data_uri("test.txt"))

    with pytest.raises(PermissionError):
        asset_repository.validate_uri("~/test.txt")


async def test_crud(asset_repository: AssetRepository) -> None:
    uri = asset_repository.generate_cache_uri("hello/test.txt")

    # delete
    await asset_repository.delete(uri)

    # get: not exists
    file_blob = await asset_repository.get(uri)
    assert file_blob is None

    # set
    await asset_repository.set(uri, "text/plain", b"test")

    # exists
    assert await asset_repository.exists(uri)

    # get: from cache
    file_blob = await asset_repository.get(uri)
    assert file_blob is not None

    # get: ignore_cache
    file_blob = await asset_repository.get(uri, ignore_cache=True)
    assert file_blob is not None

    # set: only not exists
    await asset_repository.set(uri, "text/plain", b"test2", only_not_exists=True)

    # set: only not exists and cache set
    await asset_repository.asset_cache.delete(uri)
    await asset_repository.set(uri, "text/plain", b"test2", only_not_exists=True)

    # generate_download_url
    download_url = await asset_repository.generate_download_url(uri)
    print("Generated Download URL:", download_url)
