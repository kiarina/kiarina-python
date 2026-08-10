from collections.abc import Generator

import pytest
from pydantic import BaseModel, Field

from kiarina.agi.chat_model import settings_manager
from kiarina.agi.run_context import RunContext
from kiarina.agi.structured_output import generate_model


@pytest.fixture(autouse=True)
def setup() -> Generator[None, None, None]:
    settings_manager.cli_args = {"default": "mock"}
    yield
    settings_manager.cli_args = {}


async def test_generate_model(run_context: RunContext) -> None:
    class Answer(BaseModel):
        """Answer a question"""

        answer: str = Field(description="Answer to the question")

    answer = await generate_model(
        '{"tool_calls": [{"name": "Answer", "args": {"answer": "Zeus"}}]}',
        Answer,
        run_context=run_context,
    )

    assert answer == Answer(answer="Zeus")
