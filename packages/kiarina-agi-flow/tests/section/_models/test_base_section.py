from kiarina.agi.message import HumanMessage, Message
from kiarina.agi.section import BaseSection
from kiarina.agi.tool_info import ToolInfo


def test_base_section(tool_info: ToolInfo) -> None:

    class MySection(BaseSection):
        def get_system_texts(self) -> list[str]:
            return ["You are a helpful assistant."]

        def get_messages(self) -> list[Message]:
            return [HumanMessage.create("Hello")]

        def get_tool_infos(self) -> list[ToolInfo]:
            return [tool_info]

    section = MySection()

    estimates = section.get_estimates()
    assert estimates is section.get_estimates()  # Cached
    print("__str__", str(section))
