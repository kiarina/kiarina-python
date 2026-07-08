from pathlib import Path

import pytest

from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider_impl.command import (
    CommandTTSProvider,
    CommandTTSProviderSettings,
)


@pytest.fixture
def provider() -> CommandTTSProvider:
    settings = CommandTTSProviderSettings()
    provider = CommandTTSProvider(settings)
    provider.name = "command"
    return provider


async def test_text_to_speech(
    run_context: RunContext,
    provider: CommandTTSProvider,
) -> None:
    provider.settings.command_args = {"*": ["cp", "{input_file}", "{output_file}"]}

    result = await provider.text_to_speech(
        "Hello",
        instructions="Speak clearly.",
        output_format="wav",
        run_context=run_context,
        ignore_cache=True,
    )

    assert Path(result).read_bytes() == b"Hello"


async def test_timed_out(
    run_context: RunContext,
    provider: CommandTTSProvider,
) -> None:
    provider.settings.command_args = {"*": ["sleep", "1"]}
    provider.settings.timeout = 0.1

    with pytest.raises(TimeoutError, match="Timed out"):
        await provider.text_to_speech(
            "Hello", output_format="wav", run_context=run_context
        )


async def test_failed(
    run_context: RunContext,
    provider: CommandTTSProvider,
) -> None:
    provider.settings.command_args = {"*": ["false"]}

    with pytest.raises(RuntimeError, match="Failed with exit code"):
        await provider.text_to_speech(
            "Hello", output_format="wav", run_context=run_context
        )


async def test_did_not_create(
    run_context: RunContext,
    provider: CommandTTSProvider,
) -> None:
    provider.settings.command_args = {"*": ["true"]}

    with pytest.raises(RuntimeError, match="Did not create output file"):
        await provider.text_to_speech(
            "Hello", output_format="wav", run_context=run_context
        )


async def test_unknown_command_placeholder(
    run_context: RunContext,
    provider: CommandTTSProvider,
) -> None:
    provider.settings.command_args = {"*": ["{unknown_placeholder}"]}

    with pytest.raises(ValueError, match="Unknown command placeholder"):
        await provider.text_to_speech(
            "Hello", output_format="wav", run_context=run_context
        )
