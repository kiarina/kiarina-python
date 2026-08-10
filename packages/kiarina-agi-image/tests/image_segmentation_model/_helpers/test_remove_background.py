from io import BytesIO
from pathlib import Path
from typing import Any, Literal, cast

import numpy as np
import pytest
from PIL import Image

from kiarina.agi.image_segmentation_model import remove_background
from kiarina.agi.run_context import RunContext

pytestmark = [pytest.mark.downloads_model]


@pytest.mark.parametrize(
    ("output_format", "mime_type"),
    [("png", "image/png"), ("webp", "image/webp")],
)
async def test_remove_background(
    output_format: Literal["png", "webp"],
    mime_type: str,
    test_data_dir: Path,
    run_context: RunContext,
) -> None:
    file_path = test_data_dir / "jpg/miineko2_1086x1448_219kb.jpg"

    result = await remove_background(
        str(file_path),
        output_format=output_format,
        run_context=run_context,
    )

    assert result.mime_type == mime_type
    with Image.open(BytesIO(result.raw_data)) as image:
        assert image.mode == "RGBA"
        assert image.size == (1086, 1448)
        alpha = np.array(image.getchannel("A"), dtype=np.uint8)
    assert set(np.unique(alpha)) == {0, 255}


async def test_rejects_unsupported_output_format(
    test_data_dir: Path,
    run_context: RunContext,
) -> None:
    file_path = test_data_dir / "jpg/miineko2_1086x1448_219kb.jpg"

    with pytest.raises(ValueError, match="Unsupported output format: jpeg"):
        await remove_background(
            str(file_path),
            output_format=cast(Any, "jpeg"),
            run_context=run_context,
        )
