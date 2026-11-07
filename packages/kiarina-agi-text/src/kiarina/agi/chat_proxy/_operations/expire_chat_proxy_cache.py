import os
import time


def expire_chat_proxy_cache(
    cache_dir: str | os.PathLike[str], ttl: int, *, now: float | None = None
) -> int:
    """
    Delete the files under `cache_dir` not modified for `ttl` seconds, then the
    directories left empty. Returns the number of files deleted.
    """
    if ttl <= 0 or not os.path.isdir(cache_dir):
        return 0

    deadline = (time.time() if now is None else now) - ttl
    deleted = 0

    for dir_path, _, file_names in os.walk(cache_dir, topdown=False):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)

            try:
                if os.lstat(file_path).st_mtime < deadline:
                    os.remove(file_path)
                    deleted += 1
            except FileNotFoundError:
                continue

        if os.path.realpath(dir_path) != os.path.realpath(cache_dir):
            try:
                os.rmdir(dir_path)
            except OSError:
                pass

    return deleted
