import asyncio

from _common import configure_script, read_large_text

from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.message import HumanMessage, Message
from kiarina.agi.tool_info import ToolInfo


async def main() -> None:
    run_context = configure_script()
    tool_infos = [
        ToolInfo(
            name="search",
            description="Search for information.\n\n" + read_large_text(),
            cache_control={"type": "ephemeral"},
        )
    ]
    messages: list[Message] = [HumanMessage.create("Hello, how are you?")]

    ai_message = await invoke_chat(
        messages,
        tool_infos=tool_infos,
        run_context=run_context,
    )
    messages.extend(
        [
            ai_message,
            HumanMessage.create(
                "Please provide the latest information on the OpenAI API."
            ),
        ]
    )
    await invoke_chat(messages, tool_infos=tool_infos, run_context=run_context)


if __name__ == "__main__":
    asyncio.run(main())
