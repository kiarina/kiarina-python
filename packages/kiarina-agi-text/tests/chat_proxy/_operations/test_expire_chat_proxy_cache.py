import os
from pathlib import Path

from kiarina.agi.chat_proxy import expire_chat_proxy_cache


def test_expire_chat_proxy_cache(tmp_path: Path) -> None:
    old = tmp_path / "a" / "chat_proxy" / "old"
    new = tmp_path / "b" / "new"

    for path in (old, new):
        path.parent.mkdir(parents=True)
        path.write_bytes(b"x")

    os.utime(old, (1000, 1000))
    os.utime(new, (5000, 5000))

    assert expire_chat_proxy_cache(tmp_path, 0, now=5000) == 0
    assert old.exists()

    assert expire_chat_proxy_cache(tmp_path, 2000, now=5000) == 1
    assert not old.exists()
    assert not (tmp_path / "a").exists()
    assert new.exists()
    assert tmp_path.exists()


def test_expire_chat_proxy_cache_without_dir(tmp_path: Path) -> None:
    assert expire_chat_proxy_cache(tmp_path / "missing", 10) == 0
