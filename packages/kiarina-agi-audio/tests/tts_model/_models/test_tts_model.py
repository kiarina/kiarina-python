from collections.abc import Iterator
from pathlib import Path

import pytest

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_model import TTSModel, TTSModelConfig
from kiarina.agi.tts_provider import (
    AudioFilePath,
    BaseTTSProvider,
    settings_manager,
)


class TTSProvider(BaseTTSProvider):
    def __init__(self, *args: object) -> None: ...

    last_instructions: str | None = None

    async def _text_to_speech(
        self,
        text: str,
        *,
        instructions: str | None = None,
        output_format: str | None,
        output_file_path: AudioFilePath,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> None:
        self.last_instructions = instructions

        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("test_audio")


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {"customs": {"my_provider": __name__ + ":TTSProvider"}}
    yield
    settings_manager.cli_args = {}


async def test_tts_model(run_context: RunContext) -> None:
    tts_model = TTSModel("my_model", TTSModelConfig(provider_name="my_provider"))

    result = await tts_model.text_to_speech(
        "Hello, world!",
        instructions="Speak slowly and clearly.",
        output_format="wav",
        ignore_cache=True,
        run_context=run_context,
    )

    assert result.endswith(".wav")
    assert Path(result).read_text() == "test_audio"
