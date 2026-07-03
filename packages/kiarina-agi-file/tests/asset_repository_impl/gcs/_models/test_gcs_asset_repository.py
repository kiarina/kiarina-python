import pathlib

import pytest

from kiarina.agi.file.asset_repository import AssetRepository, create_asset_repository
from kiarina.agi.file.asset_repository_impl.gcs import GCSAssetRepository


@pytest.fixture
def asset_repository(run_context) -> GCSAssetRepository:
    asset_repository = create_asset_repository(run_context)
    assert isinstance(asset_repository, GCSAssetRepository)
    return asset_repository


def test_generate_uri(asset_repository: AssetRepository) -> None:
    uri = asset_repository.generate_time_based_uri("test.txt", area="data")
    print("Generated URI (Data):", uri)
    uri = asset_repository.generate_time_based_uri("test.txt", area="cache")
    print("Generated URI (Cache):", uri)


def test_validate_uri(asset_repository: AssetRepository) -> None:
    uri = asset_repository.generate_data_uri("test.txt")

    asset_repository.validate_uri(uri)

    with pytest.raises(PermissionError):
        asset_repository.validate_uri(str(pathlib.Path(uri).parent.parent / "test.txt"))


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
