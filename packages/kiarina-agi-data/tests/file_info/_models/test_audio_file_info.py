from kiarina.agi.file_info import AudioFileInfo


def test_export() -> None:
    file_info = AudioFileInfo(
        uri_or_file_path="/path/to/file.mp3",
        mime_type="audio/mpeg",
        file_hash="dummy-hash",
        file_size=1,
        token_count=10,
        intermediate_file_path=None,
        asset_uri=None,
        duration=45.6,
        start_time=0.0,
        end_time=10.0,
    )

    exported = file_info.export()
    print("exported:", exported)

    assert "start_time" not in exported
    assert exported.get("end_time") == file_info.end_time


def test_to_content_estimates(audio_file_info: AudioFileInfo) -> None:
    estimates = audio_file_info.to_content_estimates()
    assert estimates.token_count > 0
