from kiarina.agi.asr_provider import parse_srt


def test_parse_srt() -> None:
    segments = parse_srt(
        """
1
00:00:00,000 --> 00:00:01,250
Hello.

2
00:00:01,250 --> 00:00:03,000
How are you?
""".strip()
    )

    assert len(segments) == 2
    assert segments[0].text == "Hello."
    assert segments[0].start_timestamp == 0.0
    assert segments[0].end_timestamp == 1.25
    assert segments[0].metadata == {}
    assert segments[1].text == "How are you?"
    assert segments[1].start_timestamp == 1.25
    assert segments[1].end_timestamp == 3.0


def test_parse_srt_with_speaker_name() -> None:
    segments = parse_srt(
        """
1
00:00:00,000 --> 00:00:01,250
[Speaker 1] Hello.
""".strip()
    )

    assert len(segments) == 1
    assert segments[0].text == "Hello."
    assert segments[0].metadata["speaker_name"] == "Speaker 1"


def test_parse_srt_with_webvtt_timestamp_separator() -> None:
    segments = parse_srt(
        """
00:01:02.003 --> 00:01:04.005
Hello.
""".strip()
    )

    assert len(segments) == 1
    assert segments[0].start_timestamp == 62.003
    assert segments[0].end_timestamp == 64.005


def test_parse_srt_skips_invalid_blocks() -> None:
    segments = parse_srt(
        """
This is not a subtitle block.

1
00:00:00,000 --> 00:00:01,000
Hello.
""".strip()
    )

    assert len(segments) == 1
    assert segments[0].text == "Hello."
