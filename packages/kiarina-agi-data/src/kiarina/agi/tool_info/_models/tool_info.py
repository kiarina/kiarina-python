import json
from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.token_utils import calc_text_token

from .._types.tool_name import ToolName
from .._types.tool_state import ToolState


class ToolInfo(BaseModel):
    name: ToolName
    description: str
    args_schema: dict[str, Any] = Field(default_factory=dict)
    cache_control: dict[str, Any] | None = None
    state: ToolState = "active"

    def to_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()

        text = "\n".join(
            [
                self.name,
                self.description,
                json.dumps(self.args_schema, ensure_ascii=False),
            ]
        )

        estimates.add_token_count("text", calc_text_token(text))

        return estimates

    def to_json_schema(self) -> dict[str, Any]:
        json_schema: dict[str, Any] = {
            **self.args_schema,
            "title": self.name,
            "description": self.description,
        }

        return json_schema
