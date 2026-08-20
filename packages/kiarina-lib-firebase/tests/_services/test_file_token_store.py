from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from kiarina.lib.firebase import FileTokenStore, TokenData


@pytest.fixture
def token_data() -> TokenData:
    return TokenData(
        refresh_token="refresh-token",
        id_token="id-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


async def test_round_trip(tmp_path: Path, token_data: TokenData) -> None:
    store = FileTokenStore(str(tmp_path / "token.json"))
    await store.set(token_data)

    assert await store.get() == token_data


async def test_file_not_found(tmp_path: Path) -> None:
    store = FileTokenStore(str(tmp_path / "missing.json"))

    with pytest.raises(FileNotFoundError):
        await store.get()
