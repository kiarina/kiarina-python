from typing import Any

from kiarina.agi.tool_info import ToolInfo


def to_function_definitions(tool_infos: list[ToolInfo]) -> list[dict[str, Any]]:
    """
    Convert tool infos into `{name, description, parameters}` function definitions.

    Titles are removed from the parameter schema, except property names
    that happen to be `title`.
    """
    return [_to_function_definition(tool_info) for tool_info in tool_infos]


def _to_function_definition(tool_info: ToolInfo) -> dict[str, Any]:
    parameters = _remove_titles(dict(tool_info.args_schema))
    parameters.pop("description", None)
    parameters.setdefault("type", "object")
    parameters.setdefault("properties", {})

    return {
        "name": tool_info.name,
        "description": tool_info.description,
        "parameters": parameters,
    }


def _remove_titles(schema: dict[str, Any], parent_key: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}

    for key, value in schema.items():
        if key == "title" and parent_key != "properties":
            continue

        if isinstance(value, dict):
            result[key] = _remove_titles(value, key)
        elif isinstance(value, list):
            result[key] = [
                _remove_titles(item, key) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result
