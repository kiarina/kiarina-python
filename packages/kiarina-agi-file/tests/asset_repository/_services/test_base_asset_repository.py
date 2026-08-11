from collections.abc import Iterator

import pytest

from kiarina.agi.asset_repository import (
    AssetRepository,
    URIPolicy,
    create_asset_repository,
    settings_manager,
)
from kiarina.agi.asset_repository_impl.local import LocalAssetRepository
from kiarina.agi.run_context import RunContext


@pytest.fixture()
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "uri_policy": {
            "restrict_to_repository_uris": True,
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
def asset_repository(setup: None, run_context: RunContext) -> AssetRepository:
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


def test_generate_uri_rejects_parent_traversal(
    asset_repository: AssetRepository,
) -> None:
    with pytest.raises(PermissionError):
        asset_repository.generate_data_uri("../../test.txt")


def test_validate_uri_rejects_sibling_prefix(
    asset_repository: AssetRepository,
) -> None:
    data_uri = asset_repository.generate_data_uri("test.txt").rsplit("/", 1)[0]
    sibling_uri = f"{data_uri}-other/test.txt"

    with pytest.raises(PermissionError):
        asset_repository.validate_uri(sibling_uri)


def test_validate_uri_rejects_query(
    asset_repository: AssetRepository,
) -> None:
    with pytest.raises(PermissionError):
        asset_repository.validate_uri(
            f"{asset_repository.generate_data_uri('test.txt')}?generation=1"
        )


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


def test_repositories_reject_another_run_context_uri(
    run_context: RunContext,
) -> None:
    policy = URIPolicy(
        restrict_to_repository_uris=True,
        allowed_uri_patterns=["gs://example-bucket/.*"],
        data_dir_uri_template="gs://example-bucket/data/{user_id}/{agent_id}",
        cache_dir_uri_template="gs://example-bucket/cache/{user_id}/{agent_id}",
    )
    first = LocalAssetRepository()
    first.uri_policy = policy
    first.run_context = run_context
    second = LocalAssetRepository()
    second.uri_policy = policy
    second.run_context = run_context.model_copy(
        update={"user_id": "another-user", "agent_id": "another-agent"}
    )

    with pytest.raises(PermissionError):
        first.validate_uri(second.generate_data_uri("test.txt"))


def test_containment_allows_scoped_additional_directory(
    run_context: RunContext,
) -> None:
    policy = URIPolicy(
        restrict_to_repository_uris=True,
        additional_allowed_uri_directory_templates=[
            "gs://example-bucket/users/{user_id}/uploads"
        ],
        allowed_uri_patterns=["gs://example-bucket/.*"],
        data_dir_uri_template=(
            "gs://example-bucket/users/{user_id}/spirits/{agent_id}/data"
        ),
        cache_dir_uri_template=(
            "gs://example-bucket/users/{user_id}/spirits/{agent_id}/cache"
        ),
    )
    repository = LocalAssetRepository()
    repository.uri_policy = policy
    repository.run_context = run_context.model_copy(
        update={"user_id": "user-1", "agent_id": "agent-1"}
    )

    repository.validate_uri("gs://example-bucket/users/user-1/uploads/file.txt")
    with pytest.raises(PermissionError):
        repository.validate_uri("gs://example-bucket/users/user-2/uploads/file.txt")
    with pytest.raises(PermissionError):
        repository.validate_uri(
            "gs://example-bucket/users/user-1/spirits/agent-2/data/file.txt"
        )
