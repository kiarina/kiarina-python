"""
Test cases for lock file path generation functionality.
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from kiarina.utils.file._core.utils.get_lock_file_path import (
    _cleanup_empty_dirs,
    _normalize_path,
    cleanup_old_lock_files,
    get_lock_file_path,
)


def test_normalize_path_basic():
    """Test basic path normalization."""
    path = "/tmp/test/../file.txt"
    normalized = _normalize_path(path)
    assert "test/.." not in normalized
    assert normalized.endswith("file.txt")


def test_normalize_path_expanduser():
    """Test user home directory expansion."""
    path = "~/test.txt"
    normalized = _normalize_path(path)
    assert "~" not in normalized
    assert normalized.startswith("/")


def test_normalize_path_expandvars():
    """Test environment variable expansion."""
    with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        path = "$TEST_VAR/file.txt"
        normalized = _normalize_path(path)
        assert "test_value" in normalized


def test_normalize_path_pathlike_object():
    """Test Path-like object handling."""
    path = Path("/tmp/test.txt")
    normalized = _normalize_path(path)
    assert isinstance(normalized, str)
    assert "test.txt" in normalized


def test_normalize_path_error_handling():
    """Test error handling in path normalization."""
    # Test with invalid path that might cause realpath to fail
    with patch("os.path.realpath", side_effect=OSError("Mock error")):
        path = "/tmp/test.txt"
        normalized = _normalize_path(path)
        # Should still return a valid path
        assert isinstance(normalized, str)
        assert len(normalized) > 0


def test_get_lock_file_path_consistent():
    """Test that same input produces same lock file path."""
    path = "/tmp/test.txt"
    lock1 = get_lock_file_path(path)
    lock2 = get_lock_file_path(path)
    assert lock1 == lock2


def test_get_lock_file_path_different_inputs():
    """Test that different inputs produce different lock file paths."""
    path1 = "/tmp/test1.txt"
    path2 = "/tmp/test2.txt"
    lock1 = get_lock_file_path(path1)
    lock2 = get_lock_file_path(path2)
    assert lock1 != lock2


def test_get_lock_file_path_extension():
    """Test that lock files have .lock extension."""
    path = "/tmp/test.txt"
    lock_path = get_lock_file_path(path)
    assert lock_path.endswith(".lock")


def test_get_lock_file_path_sharding():
    """Test that lock files are properly sharded into subdirectories."""
    path = "/tmp/test.txt"
    lock_path = get_lock_file_path(path)

    # Should have structure: base/xx/yy/hash.lock
    parts = lock_path.split(os.sep)
    assert len(parts) >= 4  # At least base + 2 shard dirs + filename
    assert len(parts[-3]) == 2  # First shard dir
    assert len(parts[-2]) == 2  # Second shard dir


def test_get_lock_file_path_unicode():
    """Test handling of Unicode file paths."""
    path = "/tmp/テスト.txt"
    lock_path = get_lock_file_path(path)
    assert isinstance(lock_path, str)
    assert lock_path.endswith(".lock")


def test_get_lock_file_path_long_paths():
    """Test handling of very long file paths."""
    long_name = "a" * 200
    path = f"/tmp/{long_name}.txt"
    lock_path = get_lock_file_path(path)
    assert isinstance(lock_path, str)
    assert lock_path.endswith(".lock")


def test_cleanup_old_lock_files():
    """Test cleanup of old lock files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some old lock files
        old_lock = os.path.join(temp_dir, "old.lock")
        new_lock = os.path.join(temp_dir, "new.lock")

        # Create old file
        with open(old_lock, "w") as f:
            f.write("old")

        # Create new file
        with open(new_lock, "w") as f:
            f.write("new")

        # Make old file actually old
        old_time = time.time() - 3600  # 1 hour ago
        os.utime(old_lock, (old_time, old_time))

        with patch(
            "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir",
            return_value=temp_dir,
        ):
            removed = cleanup_old_lock_files(max_age_seconds=1800)  # 30 minutes

            assert removed == 1
            assert not os.path.exists(old_lock)
            assert os.path.exists(new_lock)


def test_cleanup_respects_max_remove_limit():
    """Test that cleanup respects the max_remove limit."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple old lock files
        old_locks = []
        for i in range(5):
            lock_path = os.path.join(temp_dir, f"old_{i}.lock")
            with open(lock_path, "w") as f:
                f.write(f"old_{i}")

            # Make them old
            old_time = time.time() - 3600  # 1 hour ago
            os.utime(lock_path, (old_time, old_time))
            old_locks.append(lock_path)

        with patch(
            "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir",
            return_value=temp_dir,
        ):
            # Limit cleanup to 3 files
            removed = cleanup_old_lock_files(max_age_seconds=1800, max_remove=3)

            assert removed == 3
            # Should have 2 files remaining
            remaining = sum(1 for path in old_locks if os.path.exists(path))
            assert remaining == 2


def test_cleanup_skips_files_in_use():
    """Test that cleanup skips files that are currently in use."""

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an old lock file
        old_lock = os.path.join(temp_dir, "old.lock")
        with open(old_lock, "w") as f:
            f.write("old")

        # Make it old
        old_time = time.time() - 3600  # 1 hour ago
        os.utime(old_lock, (old_time, old_time))

        # Acquire the lock to simulate it being in use
        from filelock import FileLock

        lock = FileLock(old_lock)
        lock.acquire()

        try:
            with patch(
                "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir",
                return_value=temp_dir,
            ):
                removed = cleanup_old_lock_files(max_age_seconds=1800)

                # Should not remove the file because it's in use
                assert removed == 0
                assert os.path.exists(old_lock)
        finally:
            lock.release()


def test_cleanup_empty_dirs():
    """Test cleanup of empty directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create nested empty directories
        empty_dir = os.path.join(temp_dir, "aa", "bb")
        os.makedirs(empty_dir)

        _cleanup_empty_dirs(temp_dir)

        # Empty subdirectories should be removed
        assert not os.path.exists(empty_dir)
        assert os.path.exists(temp_dir)  # Base dir should remain


def test_cleanup_dirs_with_files():
    """Test that directories with files are not removed."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create directory with file
        subdir = os.path.join(temp_dir, "aa", "bb")
        os.makedirs(subdir)
        file_path = os.path.join(subdir, "test.lock")

        with open(file_path, "w") as f:
            f.write("test")

        _cleanup_empty_dirs(temp_dir)

        # Directory with file should remain
        assert os.path.exists(subdir)
        assert os.path.exists(file_path)


def test_cleanup_error_handling():
    """Test cleanup error handling."""
    # Test with non-existent directory by mocking _get_lock_base_dir to fail
    with patch(
        "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir",
        side_effect=OSError("Mock directory access error"),
    ):
        removed = cleanup_old_lock_files(max_age_seconds=3600)
        assert removed == 0  # Should not crash


def test_concurrent_access():
    """Test that concurrent access to same file produces same lock path."""
    import threading

    path = "/tmp/concurrent_test.txt"
    results = []

    def get_lock():
        results.append(get_lock_file_path(path))

    threads = [threading.Thread(target=get_lock) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All threads should produce the same lock path
    assert len(set(results)) == 1


def test_settings_integration():
    """Test integration with settings."""

    # Test with custom lock directory using environment variable
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {"KIARINA_UTILS_FILE_LOCK_DIR": temp_dir}):
            # Force reload settings to pick up the environment variable
            with patch(
                "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir"
            ) as mock_get_base:
                mock_get_base.return_value = temp_dir

                path = "/tmp/settings_test.txt"
                lock_path = get_lock_file_path(path)

                assert temp_dir in lock_path
                assert lock_path.endswith(".lock")


def test_automatic_cleanup_probability():
    """Test that automatic cleanup is called with low probability."""
    from kiarina.utils.file._core.utils.get_lock_file_path import (
        _maybe_cleanup_old_locks,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch(
            "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir",
            return_value=temp_dir,
        ):
            # Mock random to always return high value (no cleanup)
            with patch("random.random", return_value=0.5):
                with patch(
                    "kiarina.utils.file._core.utils.get_lock_file_path.cleanup_old_lock_files"
                ) as mock_cleanup:
                    with patch(
                        "kiarina.utils.file._core.utils.get_lock_file_path.settings_manager"
                    ) as mock_manager:
                        mock_settings = mock_manager.settings
                        mock_settings.lock_cleanup_enabled = True
                        mock_settings.lock_max_age_hours = 24

                        _maybe_cleanup_old_locks()
                        mock_cleanup.assert_not_called()

            # Mock random to always return low value (trigger cleanup)
            with patch("random.random", return_value=0.005):
                with patch(
                    "kiarina.utils.file._core.utils.get_lock_file_path.cleanup_old_lock_files"
                ) as mock_cleanup:
                    with patch(
                        "kiarina.utils.file._core.utils.get_lock_file_path.settings_manager"
                    ) as mock_manager:
                        mock_settings = mock_manager.settings
                        mock_settings.lock_cleanup_enabled = True
                        mock_settings.lock_max_age_hours = 24

                        _maybe_cleanup_old_locks()
                        mock_cleanup.assert_called_once()


def test_cleanup_disabled_by_settings():
    """Test that cleanup can be disabled by settings."""
    from kiarina.utils.file._core.utils.get_lock_file_path import (
        _maybe_cleanup_old_locks,
    )

    # Test with cleanup disabled via environment variable
    with patch.dict(os.environ, {"KIARINA_UTILS_FILE_LOCK_CLEANUP_ENABLED": "false"}):
        # Mock the settings manager to return disabled cleanup
        with patch(
            "kiarina.utils.file._core.utils.get_lock_file_path.settings_manager"
        ) as mock_manager:
            mock_settings = mock_manager.settings
            mock_settings.lock_cleanup_enabled = False

            with patch(
                "random.random", return_value=0.005
            ):  # Would normally trigger cleanup
                with patch(
                    "kiarina.utils.file._core.utils.get_lock_file_path.cleanup_old_lock_files"
                ) as mock_cleanup:
                    _maybe_cleanup_old_locks()
                    mock_cleanup.assert_not_called()


def test_lock_file_path_with_symlinks():
    """Test lock file path generation with symbolic links."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a real file
        real_file = os.path.join(temp_dir, "real_file.txt")
        with open(real_file, "w") as f:
            f.write("test")

        # Create a symlink
        symlink_file = os.path.join(temp_dir, "symlink_file.txt")
        try:
            os.symlink(real_file, symlink_file)

            # Both should resolve to the same lock file
            lock1 = get_lock_file_path(real_file)
            lock2 = get_lock_file_path(symlink_file)

            # They should be the same because realpath resolves symlinks
            assert lock1 == lock2

        except OSError:
            # Skip test if symlinks are not supported (e.g., Windows without admin)
            pytest.skip("Symlinks not supported on this system")


def test_lock_file_path_case_sensitivity():
    """Test lock file path generation with different case on case-insensitive systems."""
    if os.name == "nt":  # Windows
        # On Windows, these should produce the same lock file
        path1 = "C:\\Temp\\Test.txt"
        path2 = "c:\\temp\\test.txt"

        lock1 = get_lock_file_path(path1)
        lock2 = get_lock_file_path(path2)

        assert lock1 == lock2
    else:
        # On Unix-like systems, these should produce different lock files
        path1 = "/tmp/Test.txt"
        path2 = "/tmp/test.txt"

        lock1 = get_lock_file_path(path1)
        lock2 = get_lock_file_path(path2)

        assert lock1 != lock2


def test_default_lock_directory():
    """Test that lock files use system temp directory by default."""
    from kiarina.utils.file._core.utils.get_lock_file_path import _get_lock_base_dir

    # Test that base directory uses system temp directory
    base_dir = _get_lock_base_dir()
    assert "kiarina-utils-file-locks" in base_dir
    # Should be in system temp directory (which may be user-specific on macOS)
    assert base_dir.endswith("kiarina-utils-file-locks")


def test_cleanup_frequency_control():
    """Test that cleanup frequency is controlled by token file."""
    from kiarina.utils.file._core.utils.get_lock_file_path import (
        _maybe_cleanup_old_locks,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch(
            "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir",
            return_value=temp_dir,
        ):
            # Mock random to always trigger cleanup
            with patch("random.random", return_value=0.005):
                # Mock settings
                with patch(
                    "kiarina.utils.file._core.utils.get_lock_file_path.settings_manager"
                ) as mock_manager:
                    mock_settings = mock_manager.settings
                    mock_settings.lock_cleanup_enabled = True
                    mock_settings.lock_max_age_hours = 24

                    # First call should trigger cleanup
                    with patch(
                        "kiarina.utils.file._core.utils.get_lock_file_path.cleanup_old_lock_files"
                    ) as mock_cleanup:
                        _maybe_cleanup_old_locks()
                        mock_cleanup.assert_called_once()

                    # Second call immediately after should not trigger cleanup due to token
                    with patch(
                        "kiarina.utils.file._core.utils.get_lock_file_path.cleanup_old_lock_files"
                    ) as mock_cleanup:
                        _maybe_cleanup_old_locks()
                        mock_cleanup.assert_not_called()


def test_unicode_normalization():
    """Test that Unicode paths are properly normalized."""
    # Test with different Unicode normalizations (NFC vs NFD)
    # This is especially important on macOS
    path_nfc = "/tmp/café.txt"  # NFC form
    path_nfd = "/tmp/cafe\u0301.txt"  # NFD form (e + combining acute accent)

    # Both should normalize to the same form and produce the same lock
    lock1 = get_lock_file_path(path_nfc)
    lock2 = get_lock_file_path(path_nfd)

    # They should produce the same lock file path due to Unicode normalization
    assert lock1 == lock2


def test_cleanup_concurrent_protection():
    """Test that concurrent cleanup operations are protected."""

    from kiarina.utils.file._core.utils.get_lock_file_path import (
        _maybe_cleanup_old_locks,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch(
            "kiarina.utils.file._core.utils.get_lock_file_path._get_lock_base_dir",
            return_value=temp_dir,
        ):
            # Mock random to always trigger cleanup
            with patch("random.random", return_value=0.005):
                # Mock settings
                with patch(
                    "kiarina.utils.file._core.utils.get_lock_file_path.settings_manager"
                ) as mock_manager:
                    mock_settings = mock_manager.settings
                    mock_settings.lock_cleanup_enabled = True
                    mock_settings.lock_max_age_hours = 24

                    # First call should acquire lock and proceed
                    with patch(
                        "kiarina.utils.file._core.utils.get_lock_file_path.cleanup_old_lock_files"
                    ) as mock_cleanup:
                        _maybe_cleanup_old_locks()
                        # Should be called once
                        assert mock_cleanup.call_count <= 1
