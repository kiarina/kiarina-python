import asyncio
from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider_impl.google import (
    GoogleVideoGenerationProvider,
    GoogleVideoGenerationProviderSettings,
)


@pytest.mark.costly
async def test_google_video_generation_provider(
    cost_recorder: CostRecorder, run_context: RunContext, tmp_path: Path
) -> None:
    settings = GoogleVideoGenerationProviderSettings()
    provider = GoogleVideoGenerationProvider(settings)

    print(str(provider))
    print(f"google_auth_settings: {provider.google_auth_settings}")
    print(f"credentials: {provider.credentials}")
    print(f"client: {provider.client}")

    session_ids: list[str] = []

    # Create video
    session_id = await provider.create(
        "A cute cat playing with a ball",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    session_ids.append(session_id)

    print(f"Create session_id: {session_id}")

    try:
        # Wait for completion
        while True:
            if await provider.is_running(
                session_id,
                run_context=run_context,
            ):
                print("Video is still being generated...")
                await asyncio.sleep(10)
            else:
                break

        # Get video
        result = await provider.get(
            session_id,
            run_context=run_context,
        )

        video_path = tmp_path / result.video_mime_blob.hashed_file_name
        video_path.write_bytes(result.video_mime_blob.raw_data)

        print("---- Create Result ----")
        print(f"Video saved to: '{video_path}'")

        if result.thumbnail_mime_blob:
            thumbnail_path = tmp_path / result.thumbnail_mime_blob.hashed_file_name
            thumbnail_path.write_bytes(result.thumbnail_mime_blob.raw_data)
            print(f"Thumbnail saved to: '{thumbnail_path}'")

        if result.spritesheet_mime_blob:
            spritesheet_path = tmp_path / result.spritesheet_mime_blob.hashed_file_name
            spritesheet_path.write_bytes(result.spritesheet_mime_blob.raw_data)
            print(f"Spritesheet saved to: '{spritesheet_path}'")

        print("cost_record:")
        for record in cost_recorder.records:
            print(f" - {record}")

        assert cost_recorder.total_microdollars > 0

        cost_recorder.clear()

        # Extend video
        new_session_id = await provider.extend(
            "The cat continues playing",
            session_id=session_id,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        session_ids.append(new_session_id)

        print(f"Extend session_id: {new_session_id}")

        # Wait for completion
        while True:
            if await provider.is_running(
                new_session_id,
                run_context=run_context,
            ):
                print("Video extension is still being processed...")
                await asyncio.sleep(10)
            else:
                break

        # Get extended video
        result = await provider.get(
            new_session_id,
            run_context=run_context,
        )

        video_path = tmp_path / f"extended_{result.video_mime_blob.hashed_file_name}"
        video_path.write_bytes(result.video_mime_blob.raw_data)

        print("---- Extend Result ----")
        print(f"Video saved to: '{video_path}'")

        print("cost_record:")
        for record in cost_recorder.records:
            print(f" - {record}")

        assert cost_recorder.total_microdollars > 0

    finally:
        # Cleanup
        for session_id in session_ids:
            await provider.delete(
                session_id,
                run_context=run_context,
            )
