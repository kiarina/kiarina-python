import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from kiarina.agi.asset_cache import (
    AssetCacheSettings,
    create_asset_cache,
    settings_manager,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
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
async def test_uri(uri: str, run_context: RunContext, tmp_path: Path) -> None:
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


async def test_zero_ttl_does_not_expire(
    run_context: RunContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings_manager.cli_args = {"cache_ttl": 0}
    timestamps = iter([100.0, 1_000_000.0])
    monkeypatch.setattr(
        "kiarina.agi.asset_cache._services.asset_cache.time.time",
        lambda: next(timestamps),
    )
    asset_cache = create_asset_cache(run_context)
    uri = "https://example.com/no-expiration.txt"

    await asset_cache.delete(uri)
    await asset_cache.set(uri, "text/plain", b"hello")

    assert await asset_cache.get(uri) is not None


def test_cache_ttl_defaults_to_zero() -> None:
    assert AssetCacheSettings().cache_ttl == 0


def test_cache_ttl_rejects_negative_values() -> None:
    with pytest.raises(ValidationError):
        AssetCacheSettings(cache_ttl=-1)
