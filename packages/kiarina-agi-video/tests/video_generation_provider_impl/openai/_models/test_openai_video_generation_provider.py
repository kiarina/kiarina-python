import asyncio
from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider_impl.openai import (
    OpenAIVideoGenerationProvider,
    OpenAIVideoGenerationProviderSettings,
)


@pytest.mark.costly
async def test_openai_video_generation_provider(
    cost_recorder: CostRecorder, run_context: RunContext, tmp_path: Path
) -> None:
    settings = OpenAIVideoGenerationProviderSettings()
    provider = OpenAIVideoGenerationProvider(settings)

    print(str(provider))
    print(f"openai_settings: {provider.openai_settings}")
    print(f"client: {provider.client}")

    session_ids: list[str] = []

    session_id = await provider.create(
        "A cute cat playing with a ball",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    session_ids.append(session_id)

    print(f"Create session_id: {session_id}")

    try:
        while True:
            if await provider.is_running(
                session_id,
                run_context=run_context,
            ):
                print("Video is still being generated...")
                await asyncio.sleep(10)
            else:
                break

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

        session_id = await provider.edit(
            "Add a red ball to the scene",
            session_id=session_id,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        session_ids.append(session_id)

        print(f"Edit session_id: {session_id}")

        while True:
            if await provider.is_running(
                session_id,
                run_context=run_context,
            ):
                print("Video edit is still being processed...")
                await asyncio.sleep(10)
            else:
                break

        result = await provider.get(
            session_id,
            run_context=run_context,
        )

        video_path = tmp_path / result.video_mime_blob.hashed_file_name
        video_path.write_bytes(result.video_mime_blob.raw_data)

        print("---- Edit Result ----")
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

    finally:
        try:
            for session_id in session_ids:
                await provider.delete(
                    session_id,
                    run_context=run_context,
                )
        except Exception:
            pass
