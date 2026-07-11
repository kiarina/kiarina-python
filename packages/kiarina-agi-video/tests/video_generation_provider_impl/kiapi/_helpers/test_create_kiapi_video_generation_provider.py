from kiarina.agi.video_generation_provider_impl.kiapi import (
    create_kiapi_video_generation_provider,
)


def test_create_kiapi_video_generation_provider() -> None:
    provider = create_kiapi_video_generation_provider(
        family="ltx2",
        extra_params={"width": 512},
    )
    assert provider.settings.family == "ltx2"
    assert provider.settings.extra_params == {"width": 512}
