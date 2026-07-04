import asyncio

from _common import configure_script, read_large_text

from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.content import Content
from kiarina.agi.message import HumanMessage, Message


async def main() -> None:
    run_context = configure_script()
    content = f"<files><file>{read_large_text()}</file></files>"
    messages: list[Message] = [
        HumanMessage(
            contents=[
                Content(text=content, cache_control={"type": "ephemeral"}),
            ]
        ),
        HumanMessage.create("Hello, how are you?"),
    ]

    ai_message = await invoke_chat(messages, run_context=run_context)
    messages.extend([ai_message, HumanMessage.create("Tell me a joke.")])
    await invoke_chat(messages, run_context=run_context)


if __name__ == "__main__":
    asyncio.run(main())
