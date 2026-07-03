import asyncio
from typing import Any

import pytest

from kiarina.agi.asset_cache import create_asset_cache, settings_manager


@pytest.fixture(autouse=True)
def setup() -> Any:
    settings_manager.cli_args = {
        "cache_ttl": 1,
    }
    yield
    settings_manager.cli_args = {}


@pytest.mark.parametrize(
    "uri",
    [
        pytest.param("https://example.com/test.txt", id="1. uri"),
        pytest.param("{tmp}/test.txt", id="2. file_path"),
    ],
)
async def test_uri(uri: Any, run_context: Any, tmp_path: Any) -> None:
    uri = uri.format(tmp=str(tmp_path))

    asset_cache = create_asset_cache(run_context)

    # delete
    await asset_cache.delete(uri)

    # get: not exists
    file_blob = await asset_cache.get(uri)
    assert file_blob is None

    # set
    await asset_cache.set(uri, "text/plain", b"hello")

    # get: exists
    file_blob = await asset_cache.get(uri)
    assert file_blob is not None

    # get: expired
    await asyncio.sleep(1.1)
    file_blob = await asset_cache.get(uri)
    assert file_blob is None

    # delete: exists
    await asset_cache.delete(uri)
