import asyncio
from datetime import datetime

from _common import configure_script

from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.content import Content
from kiarina.agi.message import HumanMessage, SystemMessage
from kiarina.agi.tool_info import ToolInfo


async def main() -> None:
    run_context = configure_script()
    await invoke_chat(
        [
            SystemMessage(
                contents=[
                    Content(
                        text=(
                            "あなたは時間によって好きな果物が変わる人です。"
                            "現在時刻の分が奇数のときはりんごが好きで、"
                            "偶数のときはバナナが好きです。"
                            "ただし、30秒〜59秒の間は例外としてぶどうが好きです。"
                        )
                    ),
                    Content(text=f"現在の時刻は{datetime.now():%H:%M:%S}です。"),
                ]
            ),
            HumanMessage.create("どれが一番好き?"),
        ],
        tool_infos=[
            ToolInfo(name=name, description=description)
            for name, description in {
                "apple": "りんごが一番好きです",
                "banana": "バナナが一番好きです",
                "grape": "ぶどうが一番好きです",
            }.items()
        ],
        chat_options={"tool_choice": "any"},
        run_context=run_context,
    )


if __name__ == "__main__":
    asyncio.run(main())
