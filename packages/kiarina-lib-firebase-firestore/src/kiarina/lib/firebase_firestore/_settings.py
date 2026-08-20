from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FirestoreSettings(BaseSettings):
    """Settings for the Cloud Firestore REST client."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_FIREBASE_FIRESTORE_",
        extra="ignore",
    )

    firebase_token_manager_name: str | None = Field(
        default=None,
        title="Firebase token manager name",
        description="Name of the TokenManager to get from token_manager_registry when no token is passed.",
    )
    base_url: str = Field(
        default="https://firestore.googleapis.com",
        title="Base URL",
        description=(
            "Base URL of the Firestore REST API. "
            "Point this at a Firestore emulator for local testing."
        ),
    )
    timeout: float = Field(
        default=30.0,
        title="Request timeout",
        description="HTTP request timeout in seconds.",
    )


settings_manager = SettingsManager(FirestoreSettings)
