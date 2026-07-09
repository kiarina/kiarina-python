import os
from pathlib import Path

from kiarina.agi.file_info_builder_impl.image._operations.build_intermediate_image import (
    build_intermediate_image,
)


async def test_build_intermediate_image(
    large_image_file_path: str, tmp_path: Path
) -> None:
    output_file_path = await build_intermediate_image(
        large_image_file_path, str(tmp_path / "optimized_image")
    )

    assert output_file_path is not None

    print(f"Output file path: {output_file_path}")
    print("File size:")
    print(f"  Old: {os.path.getsize(large_image_file_path)} bytes")
    print(f"  New: {os.path.getsize(output_file_path)} bytes")
