import asyncio
from collections.abc import AsyncIterator

import pytest

from kiarina.agi.run_context import RunContext
from kiarina.agi.video_generation_provider_impl.mock import (
    MockVideoGenerationProvider,
    MockVideoGenerationProviderSettings,
    SessionStore,
)


@pytest.fixture(autouse=True)
async def clear_session_store() -> AsyncIterator[None]:
    store = SessionStore.get_instance()
    await store.clear()
    yield
    await store.clear()


def test_init_and_properties() -> None:
    settings = MockVideoGenerationProviderSettings()
    provider = MockVideoGenerationProvider(settings)

    print(str(provider))


async def test_create_video(run_context: RunContext, video_file_path: str) -> None:
    settings = MockVideoGenerationProviderSettings(
        result_video_file_path=video_file_path,
    )
    provider = MockVideoGenerationProvider(settings)

    session_id = await provider.create(
        "A beautiful sunset over the ocean",
        run_context=run_context,
    )

    print(f"session_id: {session_id}")

    try:
        # Wait for completion
        while True:
            if await provider.is_running(
                session_id,
                run_context=run_context,
            ):
                print("Video is still being generated...")
                await asyncio.sleep(0.2)
            else:
                break

        result = await provider.get(
            session_id,
            run_context=run_context,
        )

        print("---- Video Result ----")
        print(f"Video size: {len(result.video_mime_blob.raw_data)} bytes")
        print(f"Video MIME: {result.video_mime_blob.mime_type}")

        assert result.video_mime_blob.mime_type == "video/mp4"
        assert len(result.video_mime_blob.raw_data) > 0

    finally:
        await provider.delete(
            session_id,
            run_context=run_context,
        )


async def test_edit_video(run_context: RunContext, video_file_path: str) -> None:
    settings = MockVideoGenerationProviderSettings(
        result_video_file_path=video_file_path,
    )
    provider = MockVideoGenerationProvider(settings)

    session_id = await provider.create(
        "Original video",
        run_context=run_context,
    )

    while await provider.is_running(session_id, run_context=run_context):
        await asyncio.sleep(0.2)

    new_session_id = await provider.edit(
        "Add a red filter",
        session_id=session_id,
        run_context=run_context,
    )

    print(f"new_session_id: {new_session_id}")

    try:
        while await provider.is_running(new_session_id, run_context=run_context):
            await asyncio.sleep(0.2)

        result = await provider.get(
            new_session_id,
            run_context=run_context,
        )

        assert result.video_mime_blob.mime_type == "video/mp4"
        assert len(result.video_mime_blob.raw_data) > 0

    finally:
        await provider.delete(session_id, run_context=run_context)
        await provider.delete(new_session_id, run_context=run_context)


async def test_extend_video(run_context: RunContext, video_file_path: str) -> None:
    settings = MockVideoGenerationProviderSettings(
        result_video_file_path=video_file_path,
    )
    provider = MockVideoGenerationProvider(settings)

    session_id = await provider.create(
        "Original video",
        run_context=run_context,
    )

    while await provider.is_running(session_id, run_context=run_context):
        await asyncio.sleep(0.2)

    new_session_id = await provider.extend(
        "Continue the scene",
        session_id=session_id,
        run_context=run_context,
    )

    print(f"new_session_id: {new_session_id}")

    try:
        while await provider.is_running(new_session_id, run_context=run_context):
            await asyncio.sleep(0.2)

        result = await provider.get(
            new_session_id,
            run_context=run_context,
        )

        assert result.video_mime_blob.mime_type == "video/mp4"
        assert len(result.video_mime_blob.raw_data) > 0

    finally:
        await provider.delete(session_id, run_context=run_context)
        await provider.delete(new_session_id, run_context=run_context)


async def test_not_found(run_context: RunContext) -> None:
    settings = MockVideoGenerationProviderSettings()
    provider = MockVideoGenerationProvider(settings)

    session_id = "non_existent_session"

    assert not await provider.is_running(
        session_id,
        run_context=run_context,
    )

    with pytest.raises(ValueError):
        await provider.get(
            session_id,
            run_context=run_context,
        )


async def test_still_running(run_context: RunContext) -> None:
    settings = MockVideoGenerationProviderSettings(delay_seconds=10.0)
    provider = MockVideoGenerationProvider(settings)

    session_id = await provider.create(
        "Test video",
        run_context=run_context,
    )

    try:
        assert await provider.is_running(
            session_id,
            run_context=run_context,
        )

        with pytest.raises(RuntimeError):
            await provider.get(
                session_id,
                run_context=run_context,
            )

    finally:
        await provider.delete(
            session_id,
            run_context=run_context,
        )
