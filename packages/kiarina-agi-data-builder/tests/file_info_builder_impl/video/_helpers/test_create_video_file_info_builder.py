from kiarina.agi.file_info_builder_impl.video import (
    VideoFileInfoBuilder,
    create_video_file_info_builder,
)


def test_create_video_file_info_builder() -> None:
    builder = create_video_file_info_builder(
        analysis_enabled=True,
        audio_consumers=[],
        audio_event_bundlers=[],
    )

    assert isinstance(builder, VideoFileInfoBuilder)
    assert builder.settings.analysis_enabled is True
    assert builder.settings.audio_consumers == []
    assert builder.settings.audio_event_bundlers == []
