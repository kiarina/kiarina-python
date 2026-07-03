import json
from typing import Any

import ulid
from pydantic import BaseModel, Field

from kiarina.agi.data.chat_estimates import ChatEstimates
from kiarina.agi.token_utils import calc_text_token


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: ulid.new().str)
    name: str
    args: dict[str, Any] = Field(default_factory=dict)

    def to_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()

        text = "\n".join(
            [
                self.id,
                self.name,
                json.dumps(self.args, ensure_ascii=False),
            ]
        )

        estimates.add_token_count("text", calc_text_token(text))

        return estimates

    def to_text(self) -> str:
        if self.args:
            return (
                f'<tool_call name="{self.name}">\n'
                f"{json.dumps(self.args, indent=2, ensure_ascii=False)}\n"
                f"</tool_call>"
            )
        else:
            return f'<tool_call name="{self.name}" />'

    def __str__(self) -> str:
        if action := self.args.get("action"):
            return f"{self.name}:{action}"
        else:
            return f"{self.name}"
