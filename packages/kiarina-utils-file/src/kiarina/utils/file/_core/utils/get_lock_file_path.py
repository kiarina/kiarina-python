import glob
import hashlib
import os
import random
import tempfile
import time
from contextlib import suppress
from unicodedata import normalize

from filelock import FileLock, Timeout

from ..._settings import settings_manager


def get_lock_file_path(file_path: str | os.PathLike[str]) -> str:
    norm = _normalize_path(file_path)
    digest = hashlib.sha256(norm.encode("utf-8", "surrogatepass")).hexdigest()
    base = _get_lock_base_dir()

    _maybe_cleanup_old_locks()

    subdir = os.path.join(base, digest[:2], digest[2:4])
    _ensure_dir(subdir)
    return os.path.join(subdir, f"{digest}.lock")


def _maybe_cleanup_old_locks() -> None:
    settings = settings_manager.settings

    if not settings.lock_cleanup_enabled or random.random() >= 0.01:
        return

    try:
        base = _get_lock_base_dir()
    except OSError:
        return

    token_path = os.path.join(base, "cleanup.token")
    token_lock_path = token_path + ".lock"
    min_interval_seconds = 10 * 60  # 10 minutes minimum interval

    token_lock = FileLock(token_lock_path)
    try:
        token_lock.acquire(timeout=0)
    except Timeout:
        return

    try:
        last_cleanup_time = 0.0
        try:
            last_cleanup_time = os.path.getmtime(token_path)
        except FileNotFoundError:
            pass

        now = time.time()
        if now - last_cleanup_time < min_interval_seconds:
            return

        try:
            with open(token_path, "a"):
                os.utime(token_path, None)
        except Exception:
            pass

        max_age_seconds = settings.lock_max_age_hours * 3600
        max_remove = 2000  # Limit cleanup to prevent excessive I/O
        cleanup_old_lock_files(max_age_seconds=max_age_seconds, max_remove=max_remove)

    finally:
        try:
            token_lock.release()
        except Exception:
            pass


def _normalize_path(p: str | os.PathLike[str]) -> str:
    try:
        p = os.path.expandvars(os.path.expanduser(os.fspath(p)))
        p = os.path.abspath(p)

        try:
            p = os.path.realpath(p)
        except (OSError, ValueError):
            pass

        p = os.path.normpath(p)

        if os.name == "nt":
            p = os.path.normcase(p)

        p = normalize("NFC", p)

        return p
    except Exception:
        try:
            return os.path.abspath(os.fspath(p))
        except Exception:
            return str(p)


def _get_lock_base_dir() -> str:
    base = settings_manager.settings.lock_dir

    if not base:
        base = os.path.join(tempfile.gettempdir(), "kiarina-utils-file-locks")

    _ensure_dir(base)
    return base


def _ensure_dir(d: str) -> None:
    try:
        os.makedirs(d, exist_ok=True)
        try:
            os.chmod(d, 0o1777)
        except (OSError, PermissionError):
            try:
                os.chmod(d, 0o755)
            except (OSError, PermissionError):
                pass
    except OSError as e:
        raise OSError(f"Failed to create lock directory '{d}': {e}") from e


def cleanup_old_lock_files(
    max_age_seconds: int = 24 * 3600, max_remove: int | None = None
) -> int:
    try:
        base = _get_lock_base_dir()
    except OSError:
        return 0

    now = time.time()
    removed = 0

    try:
        lock_pattern = os.path.join(base, "**", "*.lock")
        for path in glob.glob(lock_pattern, recursive=True):
            try:
                if now - os.path.getmtime(path) <= max_age_seconds:
                    continue

                test_lock = FileLock(path)
                try:
                    test_lock.acquire(timeout=0)
                except Timeout:
                    continue
                else:
                    try:
                        test_lock.release()
                    except Exception:
                        pass

                with suppress(FileNotFoundError):
                    os.remove(path)

                removed += 1

                if max_remove is not None and removed >= max_remove:
                    break

            except OSError:
                continue
            except Exception:
                continue

        _cleanup_empty_dirs(base)

    except Exception:
        pass

    return removed


def _cleanup_empty_dirs(base_dir: str) -> None:
    try:
        for root, dirs, files in os.walk(base_dir, topdown=False):
            if root == base_dir:
                continue

            try:
                if not files and not dirs:
                    os.rmdir(root)
            except OSError:
                continue
    except Exception:
        pass
