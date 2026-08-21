from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FirebaseSettings(BaseSettings):
    """Settings for Firebase Authentication."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_FIREBASE_",
        extra="ignore",
    )

    api_key: SecretStr = Field(
        title="API key",
        description="Firebase Web API key.",
    )
    token_file_path: str | None = Field(
        default=None,
        title="Token file path",
        description="Path of the file that the token set is stored in.",
    )


settings_manager = SettingsManager(FirebaseSettings, multi=True)
