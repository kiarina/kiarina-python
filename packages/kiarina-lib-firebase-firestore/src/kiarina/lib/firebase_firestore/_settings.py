from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FirestoreSettings(BaseSettings):
    """Settings for the Cloud Firestore REST client."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_FIREBASE_FIRESTORE_",
        extra="ignore",
    )

    firebase_settings_key: str | None = Field(
        default=None,
        title="Firebase settings key",
        description="Key of the kiarina.lib.firebase settings whose TokenManager is used when no token is passed. The default of token_manager_registry is used when this is not set.",
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
