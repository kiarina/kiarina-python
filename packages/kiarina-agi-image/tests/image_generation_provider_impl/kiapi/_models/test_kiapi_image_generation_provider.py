from pathlib import Path

import pytest

from kiarina.agi.image_generation_provider_impl.kiapi import (
    KiapiImageGenerationProvider,
    KiapiImageGenerationProviderSettings,
    create_kiapi_image_generation_provider,
)
from kiarina.agi.run_context import RunContext

EXTRA_PARAMS = {
    "flux2": {"width": 256, "height": 256, "steps": 4},
    "qwen": {"width": 256, "height": 256, "steps": 1},
    "ernie": {"width": 256, "height": 256, "steps": 1},
}


@pytest.fixture
def provider() -> KiapiImageGenerationProvider:
    return create_kiapi_image_generation_provider()


@pytest.mark.costly
@pytest.mark.parametrize("family", ["flux2", "qwen", "ernie"])
async def test_generate_image(
    tmp_path: Path,
    run_context: RunContext,
    family: str,
) -> None:
    provider = create_kiapi_image_generation_provider(
        family=family,
        extra_params=EXTRA_PARAMS[family],
    )
    result = await provider.generate("A cat", run_context=run_context)
    assert result.mime_blob.mime_type == "image/png"

    output_path = tmp_path / f"{family}-output.png"
    output_path.write_bytes(result.mime_blob.raw_data)


@pytest.mark.costly
@pytest.mark.parametrize("family", ["flux2", "qwen", "ernie"])
async def test_edit_image(
    tmp_path: Path,
    test_data_dir: Path,
    run_context: RunContext,
    family: str,
) -> None:
    provider = create_kiapi_image_generation_provider(
        family=family,
        extra_params=EXTRA_PARAMS[family],
    )
    result = await provider.generate(
        "Change pink to blue",
        file_paths=[str(test_data_dir / "png" / "miineko_256x256_799b.png")],
        run_context=run_context,
    )
    assert result.mime_blob.mime_type == "image/png"

    output_path = tmp_path / f"{family}-edited.png"
    output_path.write_bytes(result.mime_blob.raw_data)


async def test_missing_input_file(run_context: RunContext) -> None:
    provider = KiapiImageGenerationProvider(KiapiImageGenerationProviderSettings())

    with pytest.raises(ValueError, match="does not exist"):
        await provider.generate(
            "Edit image",
            file_paths=["missing.png"],
            run_context=run_context,
        )


async def test_ernie_rejects_multiple_images(run_context: RunContext) -> None:
    provider = KiapiImageGenerationProvider(
        KiapiImageGenerationProviderSettings(family="ernie")
    )

    with pytest.raises(ValueError, match="exactly one"):
        await provider.generate(
            "Edit images",
            file_paths=["first.png", "second.png"],
            run_context=run_context,
        )
