from typing import Any

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder_impl.local import LocalCostRecorder


async def test_local_cost_recorder(run_context: Any) -> None:
    recorder = LocalCostRecorder()

    recorder.add(
        CostRecord(
            microdollars=100,
            kind="chat",
            source="test",
            metadata={"detail": "test"},
        )
    )

    await recorder.flush(run_context)

    file_blob = await kfa.read_file(recorder.file_path)
    assert file_blob is not None
    print(file_blob.raw_text)
