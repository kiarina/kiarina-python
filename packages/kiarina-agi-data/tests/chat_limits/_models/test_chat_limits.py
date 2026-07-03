from kiarina.agi.chat_limits import ChatLimits


def test_to_string() -> None:
    limits = ChatLimits(
        token_count_limit=123,
        file_size_limit=456,
        image_file_count_limit=3,
        audio_duration_limit=12.5,
        audio_file_count_limit=1,
        video_duration_limit=99.0,
        video_file_count_limit=4,
        pdf_page_count_limit=10,
        pdf_file_count_limit=5,
    )

    assert limits.token_count == "123 tokens"
    assert limits.file_size == "456 bytes"
    assert limits.image == "image(3 files)"
    assert limits.audio == "audio(1 files,12.5 sec)"
    assert limits.video == "video(4 files,99.0 sec)"
    assert limits.pdf == "pdf(5 files,10 pages)"

    assert str(limits) == limits.to_string()
    assert (
        limits.to_string() == "123 tokens 456 bytes image(3 files) "
        "audio(1 files,12.5 sec) video(4 files,99.0 sec) "
        "pdf(5 files,10 pages)"
    )


def test_from_specifier() -> None:
    assert (
        ChatLimits.from_specifier("").token_count_limit
        == ChatLimits().token_count_limit
    )
    assert ChatLimits.from_specifier("token_count_limit=1000").token_count_limit == 1000
    assert (
        ChatLimits.from_specifier('{"token_count_limit": 2000}').token_count_limit
        == 2000
    )
