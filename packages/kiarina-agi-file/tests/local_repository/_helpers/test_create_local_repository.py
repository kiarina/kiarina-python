from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext


def test_create_local_repository(run_context: RunContext) -> None:
    create_local_repository(run_context)
