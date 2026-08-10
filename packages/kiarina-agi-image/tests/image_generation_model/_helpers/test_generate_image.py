from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_generation_model import generate_image
from kiarina.agi.run_context import RunContext

pytestmark = [pytest.mark.costly]


async def test_generate_image(
    image_generation_model_name: str,
    cost_recorder: CostRecorder,
    run_context: RunContext,
    tmp_path: Path,
) -> None:
    result = await generate_image(
        "A cute cat sitting on a sofa, digital art",
        image_generation_options={
            "image_generation_model": image_generation_model_name
        },
        cost_recorder=cost_recorder,
    )

    file_path = tmp_path / result.mime_blob.hashed_file_name
    file_path.write_bytes(result.mime_blob.raw_data)

    print("---- Create Image ----")
    print(f"Image saved to: '{file_path}'")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")


async def test_generate_image_from_input(
    image_generation_model_name: str,
    cost_recorder: CostRecorder,
    run_context: RunContext,
    test_data_dir: Path,
    tmp_path: Path,
) -> None:
    result = await generate_image(
        "Add a hat to the cat",
        file_paths=[str(test_data_dir / "png" / "miineko_256x256_799b.png")],
        image_generation_options={
            "image_generation_model": image_generation_model_name
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    file_path = tmp_path / result.mime_blob.hashed_file_name
    file_path.write_bytes(result.mime_blob.raw_data)

    print("---- Generate Image ----")
    print(f"Image saved to: '{file_path}'")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")
