from typing import Literal, TypeAlias, cast

from kiarina.agi.content_builder import build_content
from kiarina.agi.file_info_loader import load_file_infos
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext

from .._types.message_input import MessageInput
from .._types.message_spec import MessageSpec

SpecType: TypeAlias = Literal["human", "ai", "tool"]


async def build_message(
    message_input: MessageInput,
    *,
    run_context: RunContext,
) -> Message:
    if isinstance(message_input, Message):
        return message_input

    elif isinstance(message_input, str):
        return _build_str("human", message_input)

    elif isinstance(message_input, dict):
        return await _build_spec("human", message_input, run_context)

    elif isinstance(message_input, tuple):
        spec_type, message_spec = message_input

        if isinstance(message_spec, str):
            return _build_str(spec_type, message_spec)

        return await _build_spec(
            spec_type, cast(MessageSpec, message_spec), run_context
        )

    else:  # pragma: no cover
        raise AssertionError(f"Invalid message input: {message_input}")


def _build_str(
    spec_type: SpecType,
    text: str,
) -> Message:
    if spec_type == "human":
        return HumanMessage.create(text)
    elif spec_type == "ai":
        return AIMessage.create(text)
    elif spec_type == "tool":  # pragma: no cover
        raise AssertionError("Tool messages cannot be created from text.")
    else:  # pragma: no cover
        raise AssertionError(f"Invalid spec_type: {spec_type}")


async def _build_spec(
    spec_type: SpecType,
    message_spec: MessageSpec,
    run_context: RunContext,
) -> Message:
    if "files" in message_spec:
        message_spec["files"] = await load_file_infos(
            message_spec["files"], run_context=run_context
        )

    content = await build_content(message_spec, run_context=run_context)

    data = {**message_spec, "contents": [content]}

    if spec_type == "human":
        return HumanMessage.model_validate(data)
    elif spec_type == "ai":
        return AIMessage.model_validate(data)
    elif spec_type == "tool":
        return ToolMessage.model_validate(data)
    else:  # pragma: no cover
        raise AssertionError(f"Invalid spec_type: {spec_type}")
