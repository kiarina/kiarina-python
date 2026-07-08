from pathlib import Path

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import AudioFilePath, BaseTTSProvider, OutputFormat


class TTSProvider(BaseTTSProvider):
    def __init__(self) -> None:
        super().__init__()
        self.call_count = 0

    async def _text_to_speech(
        self,
        text: str,
        *,
        instructions: str | None = None,
        output_format: OutputFormat,
        output_file_path: AudioFilePath,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> None:
        self.call_count += 1
        cost_recorder.add(
            CostRecord(
                microdollars=1,
                kind="tts",
                source="my_tts_provider",
            )
        )
        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("test_audio")


async def test_base_tts_provider(
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider = TTSProvider()
    provider.name = "my_tts_provider"

    result = await provider.text_to_speech(
        text="Hello, world!",
        output_format="wav",
        ignore_cache=True,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert result.endswith(".wav")
    assert Path(result).read_text() == "test_audio"
    assert cost_recorder.total_microdollars == 1

    cached_result = await provider.text_to_speech(
        text="Hello, world!",
        output_format="wav",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert cached_result == result
    assert Path(cached_result).read_text() == "test_audio"
    assert provider.call_count == 1
