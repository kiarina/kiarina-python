from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.agent_name import AgentName
from ._types.agent_specifier import AgentSpecifier


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FLOW_AGENT_",
        extra="ignore",
    )

    default: AgentSpecifier = "vanilla"

    presets: dict[AgentName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "kiarina.agi.agent_impl.vanilla:VanillaAgent",
        }
    )

    customs: dict[AgentName, ImportPath] = Field(default_factory=dict)

    max_iterations: int = 60


settings_manager = SettingsManager(AgentSettings)
