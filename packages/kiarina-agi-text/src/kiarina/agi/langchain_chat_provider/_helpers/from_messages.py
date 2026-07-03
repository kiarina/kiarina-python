from collections.abc import Sequence

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    SystemMessage,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext

from .._models.langchain_media_converter import LangChainMediaConverter
from .._operations.from_contents import from_contents
from .._types.lc_ai_message import LCAIMessage
from .._types.lc_human_message import LCHumanMessage
from .._types.lc_message import LCMessage
from .._types.lc_system_message import LCSystemMessage
from .._types.lc_tool_message import LCToolMessage


async def from_messages(
    messages: Sequence[Message],
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> list[LCMessage]:
    lc_messages: list[LCMessage] = []

    for message in messages:
        lc_messages.extend(
            await _from_messages(
                message,
                capabilities=capabilities,
                media_converter=media_converter,
                run_context=run_context,
            )
        )

    return lc_messages


async def _from_messages(
    message: Message,
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> Sequence[LCMessage]:
    if message.type == "system":
        return [
            await _from_system_message(
                message,
                capabilities=capabilities,
                media_converter=media_converter,
                run_context=run_context,
            )
        ]

    elif message.type == "human":
        return [
            await _from_human_message(
                message,
                capabilities=capabilities,
                media_converter=media_converter,
                run_context=run_context,
            )
        ]

    elif message.type == "ai":
        return [
            await _from_ai_message(
                message,
                capabilities=capabilities,
                media_converter=media_converter,
                run_context=run_context,
            )
        ]

    elif message.type == "tool":
        return await _from_tool_message(
            message,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )

    else:
        raise AssertionError(f"Unsupported message type: {message.type}")


async def _from_system_message(
    message: SystemMessage,
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> LCSystemMessage:
    result = await from_contents(
        message.type,
        message.contents,
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    return LCSystemMessage(content=result.normalized_lc_contents)


async def _from_human_message(
    message: HumanMessage,
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> LCHumanMessage:
    result = await from_contents(
        message.type,
        message.contents,
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    return LCHumanMessage(content=result.normalized_lc_contents)


async def _from_ai_message(
    message: AIMessage,
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> LCAIMessage:
    result = await from_contents(
        message.type,
        message.contents,
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    return LCAIMessage(
        content=result.normalized_lc_contents,
        tool_calls=[
            {
                "id": tool_call.id,
                "name": tool_call.name,
                "args": tool_call.args,
            }
            for tool_call in message.tool_calls
        ],
    )


async def _from_tool_message(
    message: ToolMessage,
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> Sequence[LCToolMessage | LCHumanMessage]:
    result = await from_contents(
        message.type,
        message.contents,
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    lc_messages: list[LCToolMessage | LCHumanMessage] = [
        LCToolMessage(
            content=result.normalized_lc_contents,
            tool_call_id=message.tool_call_id,
            artifact=message.artifact,
            status="error" if message.failed else "success",
        )
    ]

    if result.purged_lc_contents:
        lc_messages.append(LCHumanMessage(content=result.normalized_purged_lc_contents))

    return lc_messages
