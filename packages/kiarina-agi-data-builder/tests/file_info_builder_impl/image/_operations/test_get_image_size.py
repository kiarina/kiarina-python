from pathlib import Path

from kiarina.agi.file_info_builder_impl.image._operations.get_image_size import (
    get_image_size,
)


def test_get_image_size(test_data_dir: Path) -> None:
    raw_data = (test_data_dir / "jpg/grid_4000x3000_1400kb.jpg").read_bytes()
    image_size = get_image_size(raw_data)

    assert image_size.width == 4000
    assert image_size.height == 3000
