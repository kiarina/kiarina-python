import asyncio

from _common import configure_script

from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.message import AIMessage, HumanMessage


async def main() -> None:
    run_context = configure_script()
    await invoke_chat(
        [
            HumanMessage.create("こんにちは。"),
            AIMessage.create("最初の回答です。"),
            AIMessage.create("続けて回答します。"),
        ],
        run_context=run_context,
    )


if __name__ == "__main__":
    asyncio.run(main())
