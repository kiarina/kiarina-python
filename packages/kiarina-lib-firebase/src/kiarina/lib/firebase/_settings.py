from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FirebaseSettings(BaseSettings):
    """Settings for Firebase Authentication."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_FIREBASE_",
        extra="ignore",
    )

    project_id: str = Field(
        title="Project ID",
        description="Firebase project ID.",
    )
    api_key: SecretStr = Field(
        title="API key",
        description="Firebase Web API key.",
    )


settings_manager = SettingsManager(FirebaseSettings, multi=True)
