from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.workflow_name import WorkflowName
from ._types.workflow_specifier import WorkflowSpecifier


class WorkflowSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FLOW_WORKFLOW_",
        extra="ignore",
    )

    default: WorkflowSpecifier = "vanilla"

    presets: dict[WorkflowName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "kiarina.agi.workflow_impl.vanilla:VanillaWorkflow",
        }
    )

    customs: dict[WorkflowName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(WorkflowSettings)
