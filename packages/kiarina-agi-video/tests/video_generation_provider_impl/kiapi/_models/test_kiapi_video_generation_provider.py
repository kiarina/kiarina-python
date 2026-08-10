import asyncio
from pathlib import Path

import pytest

from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider_impl.kiapi import (
    KiapiVideoGenerationProvider,
    KiapiVideoGenerationProviderSettings,
    create_kiapi_video_generation_provider,
)

EXTRA_PARAMS = {
    "ltx2": {
        "width": 256,
        "height": 256,
        "num_frames": 9,
        "fps": 1,
    }
}


@pytest.mark.costly
@pytest.mark.parametrize("family", ["ltx2"])
async def test_generate_video(
    tmp_path: Path,
    run_context: RunContext,
    family: str,
) -> None:
    provider = create_kiapi_video_generation_provider(
        family=family,
        extra_params=EXTRA_PARAMS[family],
    )
    session_id = await provider.create("A cat", run_context=run_context)

    try:
        while await provider.is_running(session_id, run_context=run_context):
            await asyncio.sleep(1)

        result = await provider.get(session_id, run_context=run_context)
        assert result.video_mime_blob.mime_type == "video/mp4"

        output_path = tmp_path / f"{family}-output.mp4"
        output_path.write_bytes(result.video_mime_blob.raw_data)
    finally:
        await provider.delete(session_id, run_context=run_context)


async def test_missing_input_file(run_context: RunContext) -> None:
    provider = KiapiVideoGenerationProvider(KiapiVideoGenerationProviderSettings())

    with pytest.raises(ValueError, match="does not exist"):
        await provider.create(
            "A cat",
            first_image_file_path="missing.png",
            run_context=run_context,
        )


async def test_edit_and_extend_are_not_supported(run_context: RunContext) -> None:
    provider = KiapiVideoGenerationProvider(KiapiVideoGenerationProviderSettings())

    with pytest.raises(NotImplementedError, match="editing"):
        await provider.edit("Edit", session_id="job_123", run_context=run_context)
    with pytest.raises(NotImplementedError, match="extension"):
        await provider.extend("Extend", session_id="job_123", run_context=run_context)
