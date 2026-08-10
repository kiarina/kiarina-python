from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._schemas.uri_policy import URIPolicy
from ._types.asset_repository_name import AssetRepositoryName
from ._types.asset_repository_specifier import AssetRepositorySpecifier


class AssetRepositorySettings(BaseSettings):
    """Settings for resolving and restricting asset repositories."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASSET_REPOSITORY_",
        extra="ignore",
    )

    default: AssetRepositorySpecifier = Field(
        default="local",
        title="Default Repository",
        description="Repository specifier used when none is provided.",
    )

    presets: dict[AssetRepositoryName, ImportPath] = Field(
        title="Repository Presets",
        description="Built-in repository factory import paths.",
        default_factory=lambda: {
            "local": "kiarina.agi.asset_repository_impl.local:LocalAssetRepository",
            "gcs": (
                "kiarina.agi.asset_repository_impl.gcs:create_gcs_asset_repository"
            ),
        },
    )

    customs: dict[AssetRepositoryName, ImportPath] = Field(
        default_factory=dict,
        title="Custom Repositories",
        description="Custom repository factory import paths.",
    )

    uri_policy: URIPolicy = Field(
        title="URI Policy",
        description="Rules and templates used for repository URIs.",
        default_factory=lambda: URIPolicy(
            allowed_uri_patterns=[
                "{user_data_dir}/{agent_id}/asset/.*",
                "{user_cache_dir}/{agent_id}/asset/.*",
            ],
            data_dir_uri_template="{user_data_dir}/{agent_id}/asset",
            cache_dir_uri_template="{user_cache_dir}/{agent_id}/asset",
        ),
    )


settings_manager = SettingsManager(AssetRepositorySettings)
