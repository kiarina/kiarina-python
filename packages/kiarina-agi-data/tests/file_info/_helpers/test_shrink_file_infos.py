from kiarina.agi.data.file_info import TextFileInfo, shrink_file_infos


async def test_text_files() -> None:
    file_info_1 = TextFileInfo(
        uri_or_file_path="file1.txt",
        mime_type="text/plain",
        file_hash="dummy1",
        file_size=500,
        token_count=100,
        intermediate_file_path=None,
        asset_uri=None,
        line_count=20,
        raw_text="This is a sample 1\n" * 20,
    )
    file_info_2 = TextFileInfo(
        uri_or_file_path="file2.txt",
        mime_type="text/plain",
        file_hash="dummy2",
        file_size=500,
        token_count=100,
        intermediate_file_path=None,
        asset_uri=None,
        line_count=20,
        raw_text="This is a sample 2\n" * 20,
    )

    pool, reduced = shrink_file_infos([file_info_1, file_info_2], reduce=30)

    assert reduced > 0

    print("Pool:", pool)
    print("Reduced Tokens:", reduced)
