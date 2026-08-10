from pathlib import Path

import pytest

from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider_impl.mock import (
    MockTTSProvider,
    MockTTSProviderSettings,
)


@pytest.fixture
def provider() -> MockTTSProvider:
    settings = MockTTSProviderSettings()
    provider = MockTTSProvider(settings)
    provider.name = "mock"
    return provider


def test_initialize_and_properties(provider: MockTTSProvider) -> None:
    print(str(provider))


async def test_text_to_speech(
    run_context: RunContext,
    audio_file_path: str,
    provider: MockTTSProvider,
) -> None:
    provider.settings.result_audio_file_path = audio_file_path

    result = await provider.text_to_speech(
        "Hello",
        output_format="wav",
        ignore_cache=True,
        run_context=run_context,
    )

    assert Path(result).stat().st_size > 0
