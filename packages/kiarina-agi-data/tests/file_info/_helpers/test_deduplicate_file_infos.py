from datetime import datetime, timezone

from kiarina.agi.file_info import TextFileInfo, deduplicate_file_infos


def _make_text_file_info(
    path: str,
    unique_key: str | None = None,
    created_at: datetime | None = None,
) -> TextFileInfo:
    return TextFileInfo(
        uri_or_file_path=path,
        mime_type="text/plain",
        file_hash="dummy",
        file_size=100,
        token_count=10,
        intermediate_file_path=None,
        asset_uri=None,
        line_count=5,
        raw_text="hello\n" * 5,
        unique_key=unique_key,
        created_at=created_at or datetime.now(timezone.utc),
    )


def test_empty_pool() -> None:
    result = deduplicate_file_infos([])

    assert result == []


def test_no_unique_key_files_are_kept_as_is() -> None:
    fi1 = _make_text_file_info("file1.txt")
    fi2 = _make_text_file_info("file2.txt")

    result = deduplicate_file_infos([fi1, fi2])

    assert fi1 in result
    assert fi2 in result
    assert len(result) == 2


def test_unique_key_deduplication_keeps_newer() -> None:
    older = _make_text_file_info(
        "old.txt",
        unique_key="key1",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    newer = _make_text_file_info(
        "new.txt",
        unique_key="key1",
        created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )

    result = deduplicate_file_infos([older, newer])

    assert len(result) == 1
    assert result[0] is newer


def test_unique_key_deduplication_same_created_at_keeps_last_seen() -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    fi1 = _make_text_file_info("file1.txt", unique_key="key1", created_at=ts)
    fi2 = _make_text_file_info("file2.txt", unique_key="key1", created_at=ts)

    result = deduplicate_file_infos([fi1, fi2])

    assert len(result) == 1
    assert result[0] is fi2


def test_different_unique_keys_are_kept_separately() -> None:
    fi1 = _make_text_file_info("file1.txt", unique_key="key1")
    fi2 = _make_text_file_info("file2.txt", unique_key="key2")

    result = deduplicate_file_infos([fi1, fi2])

    assert len(result) == 2
    assert fi1 in result
    assert fi2 in result


def test_mix_of_unique_key_and_no_unique_key() -> None:
    no_key1 = _make_text_file_info("no_key1.txt")
    no_key2 = _make_text_file_info("no_key2.txt")
    older = _make_text_file_info(
        "old.txt",
        unique_key="key1",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    newer = _make_text_file_info(
        "new.txt",
        unique_key="key1",
        created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )

    result = deduplicate_file_infos([no_key1, older, no_key2, newer])

    assert len(result) == 3
    assert no_key1 in result
    assert no_key2 in result
    assert newer in result
    assert older not in result
