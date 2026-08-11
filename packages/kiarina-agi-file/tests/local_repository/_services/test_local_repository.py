import os
from collections.abc import Iterator

import pytest

from kiarina.agi.local_repository import (
    FilePathPolicy,
    LocalRepository,
    LocalRepositorySettings,
    create_local_repository,
    settings_manager,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture
def setup() -> Iterator[None]:
    settings_manager.cli_args = {
        "file_path_policy": {
            "restrict_to_repository_dirs": True,
            "allowed_file_path_patterns": [
                "{user_data_dir}/agents/{agent_id}/.*",
                "{user_cache_dir}/agents/{agent_id}/.*",
            ],
        }
    }
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def local_repository(setup: None, run_context: RunContext) -> LocalRepository:
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


def test_generate_path_rejects_parent_traversal(
    local_repository: LocalRepository,
) -> None:
    with pytest.raises(PermissionError):
        local_repository.generate_data_path("../../test.txt")


def test_validate_file_path_rejects_sibling_prefix(
    local_repository: LocalRepository,
) -> None:
    sibling_path = f"{local_repository.data_dir}-other/test.txt"

    with pytest.raises(PermissionError):
        local_repository.validate_file_path(sibling_path)


def test_generate_path_rejects_symlink_escape(
    local_repository: LocalRepository,
    tmp_path: os.PathLike[str],
) -> None:
    data_dir = os.path.dirname(local_repository.generate_data_path("placeholder"))
    os.makedirs(data_dir, exist_ok=True)
    symlink_path = os.path.join(data_dir, "outside")
    os.symlink(tmp_path, symlink_path)
    try:
        with pytest.raises(PermissionError):
            local_repository.generate_data_path("outside/test.txt")
    finally:
        os.unlink(symlink_path)


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


def test_repositories_reject_another_run_context_directory(
    tmp_path: os.PathLike[str],
    run_context: RunContext,
) -> None:
    settings = LocalRepositorySettings(
        file_path_policy=FilePathPolicy(
            restrict_to_repository_dirs=True,
            allowed_file_path_patterns=[".*"],
            data_dir_path_template=f"{tmp_path}/data/{{user_id}}/{{agent_id}}",
            cache_dir_path_template=f"{tmp_path}/cache/{{user_id}}/{{agent_id}}",
        )
    )
    first = LocalRepository(settings, run_context=run_context)
    second = LocalRepository(
        settings,
        run_context=run_context.model_copy(
            update={"user_id": "another-user", "agent_id": "another-agent"}
        ),
    )

    with pytest.raises(PermissionError):
        first.validate_file_path(second.generate_data_path("test.txt"))
