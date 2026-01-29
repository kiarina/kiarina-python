from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FirebaseAuthSettings(BaseSettings):
    """Firebase authentication settings."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_FIREBASE_AUTH_",
        extra="ignore",
    )


settings_manager = SettingsManager(FirebaseAuthSettings, multi=True)
