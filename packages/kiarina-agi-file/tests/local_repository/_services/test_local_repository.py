import os

import pytest

from kiarina.agi.file.local_repository import (
    LocalRepository,
    create_local_repository,
    settings_manager,
)


@pytest.fixture
def setup():
    settings_manager.cli_args = {
        "file_path_policy": {
            "allowed_file_path_patterns": [
                "{user_data_dir}/agents/{agent_id}/.*",
                "{user_cache_dir}/agents/{agent_id}/.*",
            ],
        }
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def local_repository(setup, run_context) -> LocalRepository:
    return create_local_repository(run_context)


def test_generate_time_based_file_path(local_repository: LocalRepository) -> None:
    file_path = local_repository.generate_time_based_file_path("test.txt", area="data")
    print("Generated File Path (Data):", file_path)
    file_path = local_repository.generate_time_based_file_path("test.txt", area="cache")
    print("Generated File Path (Cache):", file_path)


def test_validate_file_path(local_repository: LocalRepository) -> None:
    local_repository.validate_file_path(local_repository.generate_data_path("test.txt"))

    with pytest.raises(PermissionError):
        local_repository.validate_file_path("~/test.txt")


async def test_crud(local_repository: LocalRepository) -> None:
    file_path = local_repository.generate_cache_path("hello/test_exists.txt")

    # delete
    await local_repository.delete(file_path)

    # exists: not exists
    assert not await local_repository.exists(file_path)
    # set
    await local_repository.set(file_path, "text/plain", b"test")
    # exists
    assert await local_repository.exists(file_path)
    # exists: dir
    assert await local_repository.exists(os.path.dirname(file_path)) is False

    # set: only not exists
    await local_repository.set(file_path, "text/plain", b"test2", only_not_exists=True)

    # get
    file_blob = await local_repository.get(file_path)
    assert file_blob is not None
    assert file_blob.raw_text == "test"  # not test2
