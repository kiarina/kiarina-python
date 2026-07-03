from typing import Any

import pytest

from kiarina.utils.app import configure, single_instance
from kiarina.utils.app._exceptions.already_running_error import AlreadyRunningError
from kiarina.utils.app._settings import settings_manager


@pytest.fixture(autouse=True)
def _use_tmp_cache(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    settings_manager.user_config = {"user_cache_dir": str(tmp_path)}
    configure(app_name="kiapi", app_author="kiarina")


def test_acquire_and_release() -> None:
    single_instance.acquire()
    single_instance.release()
    # Re-acquire after release should succeed.
    single_instance.acquire()
    single_instance.release()


def test_second_acquire_raises_when_locked(tmp_path: Any) -> None:
    from filelock import FileLock

    lock_path = tmp_path / "instance.lock"
    external = FileLock(str(lock_path))
    external.acquire()
    try:
        with pytest.raises(AlreadyRunningError, match="already running"):
            single_instance.acquire(timeout=0.1)
    finally:
        external.release()
