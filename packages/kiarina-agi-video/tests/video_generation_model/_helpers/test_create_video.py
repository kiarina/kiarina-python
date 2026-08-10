import asyncio
from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_model import (
    VideoGenerationModelName,
    create_video,
    delete_video,
    edit_video,
    extend_video,
    get_video,
    is_video_running,
)

pytestmark = [pytest.mark.costly]


async def test_create_video(
    video_generation_model_name: VideoGenerationModelName,
    cost_recorder: CostRecorder,
    run_context: RunContext,
    tmp_path: Path,
) -> None:
    session_ids: list[str] = []

    session_id = await create_video(
        "A cute cat playing with a ball",
        video_generation_options={
            "video_generation_model": video_generation_model_name
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )
    session_ids.append(session_id)
    print(f"session_id: {session_id}")

    try:
        while True:
            if await is_video_running(
                session_id,
                video_generation_options={
                    "video_generation_model": video_generation_model_name
                },
                run_context=run_context,
            ):
                print("Video is still being generated...")
                await asyncio.sleep(10)
            else:
                break

        result = await get_video(
            session_id,
            video_generation_options={
                "video_generation_model": video_generation_model_name
            },
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

        cost_recorder.clear()

        try:
            session_id = await edit_video(
                "Add a red ball to the scene",
                session_id=session_id,
                video_generation_options={
                    "video_generation_model": video_generation_model_name
                },
                cost_recorder=cost_recorder,
                run_context=run_context,
            )

            session_ids.append(session_id)

            print(f"Edit session_id: {session_id}")

            while True:
                if await is_video_running(
                    session_id,
                    video_generation_options={
                        "video_generation_model": video_generation_model_name
                    },
                    run_context=run_context,
                ):
                    print("Video edit is still being processed...")
                    await asyncio.sleep(10)
                else:
                    break

            result = await get_video(
                session_id,
                video_generation_options={
                    "video_generation_model": video_generation_model_name
                },
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
                spritesheet_path = (
                    tmp_path / result.spritesheet_mime_blob.hashed_file_name
                )
                spritesheet_path.write_bytes(result.spritesheet_mime_blob.raw_data)
                print(f"Spritesheet saved to: '{spritesheet_path}'")

            print("cost_record:")
            for record in cost_recorder.records:
                print(f" - {record}")

            cost_recorder.clear()

        except NotImplementedError:
            print("Edit video not supported for this video model.")

        try:
            session_id = await extend_video(
                "Extend the video by adding more playful actions",
                session_id=session_id,
                video_generation_options={
                    "video_generation_model": video_generation_model_name
                },
                cost_recorder=cost_recorder,
                run_context=run_context,
            )

            session_ids.append(session_id)

            print(f"Extend session_id: {session_id}")

            while True:
                if await is_video_running(
                    session_id,
                    video_generation_options={
                        "video_generation_model": video_generation_model_name
                    },
                    run_context=run_context,
                ):
                    print("Video extension is still being processed...")
                    await asyncio.sleep(10)
                else:
                    break

            result = await get_video(
                session_id,
                video_generation_options={
                    "video_generation_model": video_generation_model_name
                },
                run_context=run_context,
            )

            video_path = tmp_path / result.video_mime_blob.hashed_file_name
            video_path.write_bytes(result.video_mime_blob.raw_data)

            print("---- Extend Result ----")
            print(f"Video saved to: '{video_path}'")

            if result.thumbnail_mime_blob:
                thumbnail_path = tmp_path / result.thumbnail_mime_blob.hashed_file_name
                thumbnail_path.write_bytes(result.thumbnail_mime_blob.raw_data)
                print(f"Thumbnail saved to: '{thumbnail_path}'")

            if result.spritesheet_mime_blob:
                spritesheet_path = (
                    tmp_path / result.spritesheet_mime_blob.hashed_file_name
                )
                spritesheet_path.write_bytes(result.spritesheet_mime_blob.raw_data)
                print(f"Spritesheet saved to: '{spritesheet_path}'")

            print("cost_record:")
            for record in cost_recorder.records:
                print(f" - {record}")

        except NotImplementedError:
            print("Extend video not supported for this video model.")

    finally:
        for session_id in session_ids:
            try:
                await delete_video(
                    session_id,
                    video_generation_options={
                        "video_generation_model": video_generation_model_name
                    },
                    run_context=run_context,
                )
            except Exception:
                pass
