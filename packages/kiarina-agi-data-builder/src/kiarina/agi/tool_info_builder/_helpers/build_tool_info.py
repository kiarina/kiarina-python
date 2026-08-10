from typing import cast

from pydantic import ValidationError

from kiarina.agi.tool import tool_registry
from kiarina.agi.tool_info import ToolInfo, ToolState
from kiarina.i18n import Language

from .._types.tool_info_specifier import ToolInfoSpecifier


def build_tool_info(
    specifier: ToolInfoSpecifier,
    *,
    language: Language,
) -> ToolInfo:
    if specifier.startswith("{"):
        try:
            return ToolInfo.model_validate_json(specifier)
        except ValidationError as e:  # pragma: no cover
            raise ValueError(f"Invalid JSON for tool info: {specifier}") from e

    if ":" in specifier:
        state, name = specifier.split(":", 1)

        if state not in ("active", "inactive", "disabled"):  # pragma: no cover
            raise ValueError(
                f"Invalid tool state in specifier: {state}. "
                f"Expected one of: active, inactive, disabled."
            )

        tool = tool_registry.resolve(name)
        tool_info = tool.to_tool_info(language)
        tool_info.state = cast(ToolState, state)

        return tool_info

    tool = tool_registry.resolve(specifier)
    tool_info = tool.to_tool_info(language)

    return tool_info
