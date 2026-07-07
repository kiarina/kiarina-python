from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_provider_impl.google import (
    GoogleImageGenerationProvider,
    GoogleImageGenerationProviderSettings,
)
from kiarina.agi.run_context import RunContext


@pytest.mark.costly
async def test_google_image_generation_provider(
    cost_recorder: CostRecorder, run_context: RunContext, tmp_path: Path
) -> None:
    settings = GoogleImageGenerationProviderSettings()
    provider = GoogleImageGenerationProvider(settings)

    print(str(provider))
    print(f"client: {provider.client}")

    result = await provider.generate(
        prompt="A cute cat sitting on a sofa, digital art",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    file_path = tmp_path / result.mime_blob.hashed_file_name
    file_path.write_bytes(result.mime_blob.raw_data)

    print("---- Create Image ----")
    print(f"Image saved to: '{file_path}'")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    cost_recorder.clear()

    result = await provider.generate(
        prompt="Add a hat to the cat",
        file_paths=[str(file_path)],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    edited_file_path = tmp_path / f"edited_{result.mime_blob.hashed_file_name}"
    edited_file_path.write_bytes(result.mime_blob.raw_data)

    print("---- Edit Image ----")
    print(f"Edited image saved to: '{edited_file_path}'")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")
