from filelock import FileLock, Timeout

from .._exceptions.already_running_error import AlreadyRunningError
from .._instances.app import app
from .user_directory import get_user_cache_dir

_LOCK_FILE = "instance.lock"
_lock: FileLock | None = None


def acquire(*, timeout: float = 10.0) -> None:
    global _lock

    cache_dir = get_user_cache_dir()
    path = cache_dir / _LOCK_FILE

    if _lock is None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        _lock = FileLock(str(path))

    try:
        _lock.acquire(timeout=timeout)
    except Timeout as exc:
        raise AlreadyRunningError(
            f"another {app.app_name} instance is already running (lock: {path})"
        ) from exc


def release() -> None:
    global _lock

    if _lock is not None:
        _lock.release()
        _lock = None
