import pytest

from kiarina.agi.file.asset_repository import URIPolicy
from kiarina.agi.file.asset_repository_impl.local import LocalAssetRepository


@pytest.fixture
def asset_repository(run_context) -> LocalAssetRepository:
    repository = LocalAssetRepository()
    repository.uri_policy = URIPolicy(
        allowed_uri_patterns=[".*"],
        data_dir_uri_template="{user_data_dir}/{agent_id}/asset",
        cache_dir_uri_template="{user_cache_dir}/{agent_id}/asset",
    )
    repository.run_context = run_context
    return repository


def test_template_variables(asset_repository) -> None:
    print("Template Variables:", asset_repository.template_variables)
