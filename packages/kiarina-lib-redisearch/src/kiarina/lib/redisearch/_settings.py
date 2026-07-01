from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class RedisearchSettings(BaseSettings):
    """Settings for a RediSearch index."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_REDISEARCH_")

    key_prefix: str = Field(
        default="",
        title="Key Prefix",
        description="Prefix for document keys, such as 'myapp:'.",
    )
    index_name: str = Field(
        default="default",
        title="Index Name",
        description="Name of the RediSearch index.",
    )
    protect_index_deletion: bool = Field(
        default=False,
        title="Protect Index Deletion",
        description="Prevent the client from dropping the index.",
    )


settings_manager = SettingsManager(RedisearchSettings, multi=True)
