from kiarina.agi.file.asset_repository_impl.gcs import create_gcs_asset_repository


def test_create_asset_repository() -> None:
    _ = create_gcs_asset_repository()
    assert True
