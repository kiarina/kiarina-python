from kiarina.lib.google.cloud_storage import get_storage_client


def test_get_storage_client():
    client = get_storage_client()
    assert client is not None
