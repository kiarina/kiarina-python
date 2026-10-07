from typing import TYPE_CHECKING

from kiarina.agi.message import AIMessage, ToolCall

from .._schemas.openai_chat_result import OpenAIChatResult
from .from_completion_usage import from_completion_usage
from .from_finish_reason import from_finish_reason
from .parse_tool_call_args import parse_tool_call_args

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletion


def from_chat_completion(completion: "ChatCompletion") -> OpenAIChatResult:
    choice = completion.choices[0]
    message = choice.message

    return OpenAIChatResult(
        ai_message=AIMessage.create(
            text=message.content or message.refusal or "",
            tool_calls=[
                ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    args=parse_tool_call_args(tool_call.function.arguments),
                )
                for tool_call in message.tool_calls or []
                if tool_call.type == "function"
            ],
        ),
        stop_reason=from_finish_reason(choice.finish_reason),
        usage=from_completion_usage(completion.usage),
    )
