from kiarina.agi.image_generation_provider_impl.kiapi import (
    create_kiapi_image_generation_provider,
)


def test_create_kiapi_image_generation_provider() -> None:
    provider = create_kiapi_image_generation_provider(
        family="flux2",
        extra_params={"width": 512},
    )
    assert provider.settings.family == "flux2"
    assert provider.settings.extra_params == {"width": 512}
