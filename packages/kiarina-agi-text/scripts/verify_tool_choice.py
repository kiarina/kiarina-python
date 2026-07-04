import asyncio

from _common import configure_script

from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.message import HumanMessage
from kiarina.agi.tool_info import ToolInfo


async def main() -> None:
    run_context = configure_script()
    tool_infos = [
        ToolInfo(name=name, description=description)
        for name, description in {
            "apple": "りんごが一番好きです",
            "banana": "バナナが一番好きです",
            "grape": "ぶどうが一番好きです",
        }.items()
    ]
    await invoke_chat(
        [HumanMessage.create("どれが一番好き?")],
        tool_infos=tool_infos,
        chat_options={"tool_choice": "any"},
        run_context=run_context,
    )


if __name__ == "__main__":
    asyncio.run(main())
