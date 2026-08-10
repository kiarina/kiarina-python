from kiarina.agi.file_info_loader import load_file_infos
from kiarina.agi.run_context import RunContext


async def test_load_file_infos(run_context: RunContext, text_file_path: str) -> None:
    file_infos = await load_file_infos(
        [text_file_path, "not-found.txt"],
        run_context=run_context,
    )

    assert len(file_infos) == 1
    print(file_infos[0].model_dump_json(indent=2))
