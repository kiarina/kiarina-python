from kiarina.agi.video_generation_provider_impl.mock import (
    MockVideoGenerationProvider,
    create_mock_video_generation_provider,
)


def test_create_mock_video_generation_provider() -> None:
    provider = create_mock_video_generation_provider(
        result_video_file_path="path/to/mock_video.mp4",
    )
    assert isinstance(provider, MockVideoGenerationProvider)
    assert provider.settings.result_video_file_path == "path/to/mock_video.mp4"
