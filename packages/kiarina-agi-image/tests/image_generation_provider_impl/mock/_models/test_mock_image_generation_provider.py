from pathlib import Path

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_provider_impl.mock import (
    MockImageGenerationProvider,
    MockImageGenerationProviderSettings,
)
from kiarina.agi.run_context import RunContext

# --------------------------------------------------
# Initialization and Properties
# --------------------------------------------------


def test_initialize_and_properties() -> None:
    settings = MockImageGenerationProviderSettings()
    provider = MockImageGenerationProvider(settings)

    print(str(provider))


# --------------------------------------------------
# Create Image
# --------------------------------------------------


async def test_generate_image(run_context: RunContext) -> None:
    settings = MockImageGenerationProviderSettings(
        image_width=512,
        image_height=512,
        color=(255, 100, 50),
    )
    provider = MockImageGenerationProvider(settings)

    result = await provider.generate(
        "A beautiful sunset",
        run_context=run_context,
    )

    assert result.mime_blob.mime_type == "image/png"
    assert len(result.mime_blob.raw_data) > 0


async def test_generate_image_jpeg_format(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    settings = MockImageGenerationProviderSettings(
        output_format="jpeg",
    )
    provider = MockImageGenerationProvider(settings)

    result = await provider.generate(
        "Test image",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert result.mime_blob.mime_type == "image/jpeg"
    assert len(result.mime_blob.raw_data) > 0


# --------------------------------------------------
# Edit Image
# --------------------------------------------------


async def test_generate_image_from_input(
    run_context: RunContext, tmp_path: Path
) -> None:
    settings = MockImageGenerationProviderSettings()
    provider = MockImageGenerationProvider(settings)

    # First create an image
    create_result = await provider.generate(
        "Original image",
        run_context=run_context,
    )

    # Save to file
    image_path = tmp_path / "test_image.png"
    image_path.write_bytes(create_result.mime_blob.raw_data)

    # Edit the image
    edit_result = await provider.generate(
        "Add a red border",
        file_paths=[str(image_path)],
        run_context=run_context,
    )

    assert edit_result.mime_blob.mime_type == "image/png"
    assert len(edit_result.mime_blob.raw_data) > 0
