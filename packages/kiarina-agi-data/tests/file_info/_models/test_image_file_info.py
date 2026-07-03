from kiarina.agi.data.file_info import ImageFileInfo


def test_to_content_estimates(image_file_info: ImageFileInfo) -> None:
    estimates = image_file_info.to_content_estimates()
    assert estimates.token_count > 0
