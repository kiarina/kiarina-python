from kiarina.agi.tool_info import ToolName

from .._schemas.additional_field_config import AdditionalFieldConfig
from .._settings import settings_manager


def get_additional_fields(
    tool_name: ToolName,
) -> list[AdditionalFieldConfig]:
    settings = settings_manager.get_settings()

    return [
        field_config
        for field_config in settings.additional_fields
        if field_config.should_apply_to(tool_name)
    ]
