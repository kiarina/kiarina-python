from typing import Any

from kiarina.agi.tool_info import ToolInfo


def to_function_declarations(tool_infos: list[ToolInfo]) -> list[dict[str, Any]]:
    declarations: list[dict[str, Any]] = []

    for tool_info in tool_infos:
        parameters = {
            k: v
            for k, v in tool_info.args_schema.items()
            if k not in ("title", "description")
        }
        parameters.setdefault("type", "object")
        parameters.setdefault("properties", {})

        declarations.append(
            {
                "name": tool_info.name,
                "description": tool_info.description,
                "parameters_json_schema": parameters,
            }
        )

    return declarations
