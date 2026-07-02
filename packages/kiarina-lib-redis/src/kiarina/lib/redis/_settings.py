from typing import Any

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class RedisSettings(BaseSettings):
    """Redis client settings."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_REDIS_")

    url: SecretStr = Field(
        default=SecretStr("redis://localhost:6379"),
        title="Redis URL",
        description="Redis connection URL.",
    )

    initialize_params: dict[str, Any] = Field(
        default_factory=dict,
        title="Initialization Parameters",
        description="Additional parameters passed to Redis.from_url().",
    )

    use_retry: bool = Field(
        default=False,
        title="Use Retry",
        description="Retry Redis connection and timeout errors.",
    )

    socket_timeout: float = Field(
        default=6.0,
        title="Socket Timeout",
        description="Socket read and write timeout in seconds when retries are enabled.",
    )

    socket_connect_timeout: float = Field(
        default=3.0,
        title="Socket Connection Timeout",
        description="Socket connection timeout in seconds when retries are enabled.",
    )

    health_check_interval: int = Field(
        default=60,
        title="Health Check Interval",
        description="Connection health check interval in seconds when retries are enabled.",
    )

    retry_attempts: int = Field(
        default=3,
        title="Retry Attempts",
        description="Number of retry attempts.",
    )

    retry_delay: float = Field(
        default=1.0,
        title="Retry Delay",
        description="Maximum exponential backoff delay in seconds.",
    )


settings_manager = SettingsManager(RedisSettings, multi=True)
"""Manager for named Redis client settings."""
