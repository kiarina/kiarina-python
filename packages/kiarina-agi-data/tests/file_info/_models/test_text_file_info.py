from kiarina.agi.data.file_info import TextFileInfo


def test_export() -> None:
    file_info = TextFileInfo(
        uri_or_file_path="/path/to/file.txt",
        mime_type="text/plain",
        file_hash="dummy-hash",
        file_size=1,
        token_count=10,
        intermediate_file_path=None,
        asset_uri=None,
        line_count=3,
        raw_text="Line 2\nLine 3",
        start_line=2,
        end_line=-1,
    )

    exported = file_info.export()
    print("exported:", exported)

    assert exported.get("start_line") == file_info.start_line
    assert "end_line" not in exported


def test_to_content_estimates(text_file_info: TextFileInfo) -> None:
    estimates = text_file_info.to_content_estimates()
    assert estimates.token_count > 0


def test_shrink(text_file_info) -> None:
    # metadata only
    new_file_info, reduced = text_file_info.shrink(
        reduce=text_file_info.token_count + 1
    )
    assert new_file_info.metadata_only
    assert reduced == text_file_info.token_count

    # normal reduce
    new_file_info, reduced = text_file_info.shrink(reduce=10)
    assert new_file_info is not text_file_info
    assert reduced >= 10

    # over reduce
    new_file_info, reduced = text_file_info.shrink(
        reduce=text_file_info.token_count - 1
    )
    assert new_file_info.metadata_only
    assert reduced == text_file_info.token_count


def test_shrink_by_line(text_file_info) -> None:
    # keep_from_start
    new_file_info = text_file_info.shrink_by_line(keep_line_count=2)
    assert new_file_info.normalized_end_line < text_file_info.line_count
    assert new_file_info.segment_line_count == 2
    print("--- keep_from_start ---")
    print(new_file_info.model_dump_json(indent=2))

    # keep_from_end
    text_file_info.keep_from_end = True
    new_file_info = text_file_info.shrink_by_line(keep_line_count=2)
    assert new_file_info.normalized_start_line > 1
    assert new_file_info.segment_line_count == 2
    print("--- keep_from_end ---")
    print(new_file_info.model_dump_json(indent=2))
