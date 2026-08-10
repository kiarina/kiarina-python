import subprocess
from pathlib import Path

import pytest

from kiarina.agi.local_scanner import scan_directory


def test_not_exist() -> None:
    with pytest.raises(FileNotFoundError):
        scan_directory("/path/that/does/not/exist")


def test_not_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("This is a file, not a directory.")

    with pytest.raises(NotADirectoryError):
        scan_directory(file_path)


def test_basic(tmp_path: Path) -> None:
    (tmp_path / "file1.txt").write_text("File 1")
    (tmp_path / "file2.py").write_text("File 2")
    (tmp_path / "file3.md").write_text("File 3")

    dir_a = tmp_path / "dir_a"
    dir_a.mkdir()
    (dir_a / "file_a1.txt").write_text("File A1")
    (dir_a / "file_a2.py").write_text("File A2")

    dir_b = tmp_path / "dir_b"
    dir_b.mkdir()
    (dir_b / "file_b1.md").write_text("File B1")

    sub_dir = dir_b / "sub_dir"
    sub_dir.mkdir()
    (sub_dir / "file_b2.txt").write_text("File B2")

    dir_c = tmp_path / ".dir_c"
    dir_c.mkdir()
    (dir_c / "file_c1.txt").write_text("File C1")

    file_paths = scan_directory(tmp_path)

    rel_paths = sorted(
        [str(path.relative_to(tmp_path)) for path in [tmp_path / p for p in file_paths]]
    )

    assert len(rel_paths) == 8
    assert "file1.txt" in rel_paths
    assert "file2.py" in rel_paths
    assert "file3.md" in rel_paths
    assert "dir_a/file_a1.txt" in rel_paths
    assert "dir_a/file_a2.py" in rel_paths
    assert "dir_b/file_b1.md" in rel_paths
    assert "dir_b/sub_dir/file_b2.txt" in rel_paths
    assert ".dir_c/file_c1.txt" in rel_paths


def test_include_patterns(tmp_path: Path) -> None:
    (tmp_path / "file1.txt").write_text("File 1")
    (tmp_path / "file2.py").write_text("File 2")
    (tmp_path / "file3.md").write_text("File 3")

    dir_a = tmp_path / "dir_a"
    dir_a.mkdir()
    (dir_a / "file_a1.txt").write_text("File A1")
    (dir_a / "file_a2.py").write_text("File A2")

    file_paths = scan_directory(tmp_path, include_patterns=["*.txt"])

    assert len(file_paths) == 2
    assert any("file1.txt" in path for path in file_paths)
    assert any("file_a1.txt" in path for path in file_paths)


def test_exclude_patterns(tmp_path: Path) -> None:
    (tmp_path / "file1.txt").write_text("File 1")
    (tmp_path / "file2.py").write_text("File 2")
    (tmp_path / "file3.md").write_text("File 3")

    dir_a = tmp_path / "dir_a"
    dir_a.mkdir()
    (dir_a / "file_a1.txt").write_text("File A1")
    (dir_a / "file_a2.py").write_text("File A2")

    file_paths = scan_directory(tmp_path, exclude_patterns=["*.py"])

    assert len(file_paths) == 3
    assert not any("file2.py" in path for path in file_paths)
    assert not any("file_a2.py" in path for path in file_paths)


def test_include_and_exclude_patterns(tmp_path: Path) -> None:
    (tmp_path / "file1.txt").write_text("File 1")
    (tmp_path / "file2.py").write_text("File 2")
    (tmp_path / "test.txt").write_text("Test")

    dir_a = tmp_path / "dir_a"
    dir_a.mkdir()
    (dir_a / "file_a1.txt").write_text("File A1")
    (dir_a / "test_a.txt").write_text("Test A")

    file_paths = scan_directory(
        tmp_path,
        include_patterns=["*.txt"],
        exclude_patterns=["test*"],
    )

    assert len(file_paths) == 2
    assert any("file1.txt" in path for path in file_paths)
    assert any("file_a1.txt" in path for path in file_paths)


def test_gitignore(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log\ntemp/\n")

    (tmp_path / "file1.txt").write_text("File 1")
    (tmp_path / "debug.log").write_text("Debug log")

    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "temp_file.txt").write_text("Temp file")

    file_paths = scan_directory(tmp_path)

    assert len(file_paths) == 2
    assert any(".gitignore" in path for path in file_paths)
    assert any("file1.txt" in path for path in file_paths)


def test_relative_path_patterns(tmp_path: Path) -> None:
    dir_a = tmp_path / "dir_a"
    dir_a.mkdir()
    (dir_a / "file1.txt").write_text("File 1")

    dir_b = tmp_path / "dir_b"
    dir_b.mkdir()
    (dir_b / "file2.txt").write_text("File 2")

    file_paths = scan_directory(tmp_path, include_patterns=["dir_a/*"])

    assert len(file_paths) == 1
    assert "dir_a/file1.txt" in str((tmp_path / file_paths[0]).relative_to(tmp_path))
