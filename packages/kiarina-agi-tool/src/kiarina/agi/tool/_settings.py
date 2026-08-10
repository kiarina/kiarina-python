from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.tool_info import ToolName
from kiarina.utils.common import ImportPath

from ._schemas.additional_field_config import AdditionalFieldConfig


class ToolSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TOOL_",
        extra="ignore",
    )

    presets: dict[ToolName, ImportPath] = Field(
        default_factory=lambda: {
            "exit": "kiarina.agi.tool_impl.exit:ExitTool",
            "finish": "kiarina.agi.tool_impl.finish:FinishTool",
            "hello": "kiarina.agi.tool_impl.hello:HelloTool",
            "wait": "kiarina.agi.tool_impl.wait:WaitTool",
        }
    )

    customs: dict[ToolName, ImportPath] = Field(default_factory=dict)

    additional_fields: list[AdditionalFieldConfig] = Field(
        default_factory=lambda: [
            AdditionalFieldConfig(
                name="reason",
                type_hint="str",
                description="Reasons for running this tool",
                i18n_scope="kiarina.agi.tool",
                i18n_key="reason_desc",
            ),
            # AdditionalFieldConfig(
            #     name="expect",
            #     type_hint="str",
            #     description="Expected results from running this tool",
            #     i18n_scope="kiarina.agi.tool",
            #     i18n_key="expect_desc",
            # ),
        ]
    )


settings_manager = SettingsManager(ToolSettings)
