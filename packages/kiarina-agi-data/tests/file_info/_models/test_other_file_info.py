from kiarina.agi.file_info import OtherFileInfo


def test_to_content_estimates(other_file_info: OtherFileInfo) -> None:
    estimates = other_file_info.to_content_estimates()
    assert estimates.token_count == 0
