from kiarina.agi.section import BaseSection
from kiarina.agi.tool_info import ToolInfo


class ToolSection(BaseSection):
    def get_tool_infos(self) -> list[ToolInfo]:
        return self.ctx.history.get_tool_infos(state="active")
