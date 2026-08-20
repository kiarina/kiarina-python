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
    token_data_file_path: str | None = Field(
        default=None,
        title="Token data file path",
        description="Path of the file that token_manager_registry stores the token set in.",
    )


settings_manager = SettingsManager(FirebaseSettings, multi=True)
