import json
from collections.abc import Generator
from datetime import date

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

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


async def test_strict_schema_accepts_json_tuple_and_date(
    run_context: RunContext,
) -> None:
    class Answer(BaseModel):
        """Return a dated pair of labels."""

        model_config = ConfigDict(strict=True)
        labels: tuple[str, str] = Field(description="Two labels")
        recorded_on: date = Field(description="The recorded date")

    answer = await generate_model(
        json.dumps(
            {
                "tool_calls": [
                    {
                        "name": "Answer",
                        "args": {
                            "labels": ["喜び", "希望"],
                            "recorded_on": "2026-11-04",
                        },
                    }
                ]
            },
            ensure_ascii=False,
        ),
        Answer,
        run_context=run_context,
    )
    assert answer.labels == ("喜び", "希望")
    assert answer.recorded_on == date(2026, 11, 4)


async def test_multiple_tool_calls_use_the_first(run_context: RunContext) -> None:
    class Answer(BaseModel):
        """Return an answer."""

        answer: str = Field(description="Answer text")

    result = await generate_model(
        json.dumps(
            {
                "tool_calls": [
                    {"name": "Answer", "args": {"answer": "first"}},
                    {"name": "Answer", "args": {}},
                ]
            }
        ),
        Answer,
        run_context=run_context,
    )
    assert result.answer == "first"


async def test_invalid_first_call_is_not_replaced_by_a_later_one(
    run_context: RunContext,
) -> None:
    class Answer(BaseModel):
        """Return a strict integer."""

        model_config = ConfigDict(strict=True)
        value: int = Field(description="An integer value")

    with pytest.raises(ValidationError) as error:
        await generate_model(
            json.dumps(
                {
                    "tool_calls": [
                        {"name": "Answer", "args": {"value": "3"}},
                        {"name": "Answer", "args": {"value": 3}},
                    ]
                }
            ),
            Answer,
            run_context=run_context,
        )
    assert error.value.errors()[0]["type"] == "int_type"
