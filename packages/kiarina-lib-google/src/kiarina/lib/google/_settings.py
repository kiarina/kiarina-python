import json
import os
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class GoogleSettings(BaseSettings):
    """Google authentication settings."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_LIB_GOOGLE_")

    type: Literal["default", "service_account", "user_account", "api_key"] = Field(
        default="default",
        title="Authentication Type",
        description="Authentication method to use.",
    )

    # --------------------------------------------------
    # Fields (common)
    # --------------------------------------------------

    project_id: str | None = Field(
        default=None,
        title="Project ID",
        description="Google Cloud project ID.",
    )

    impersonate_service_account: str | None = Field(
        default=None,
        title="Service Account to Impersonate",
        description=(
            "Email address of the service account to impersonate. The source "
            "principal requires roles/iam.serviceAccountTokenCreator."
        ),
    )

    scopes: list[str] = Field(
        default_factory=list,
        title="Scopes",
        description="OAuth scopes to request.",
    )

    # --------------------------------------------------
    # Fields (service_account)
    # --------------------------------------------------

    service_account_email: str | None = Field(
        default=None,
        title="Service Account Email",
        description="Service account email address.",
    )

    service_account_file: str | None = Field(
        default=None,
        title="Service Account File",
        description="Path to a service account key file.",
    )

    service_account_data: SecretStr | None = Field(
        default=None,
        title="Service Account Data",
        description="Service account key data as a JSON string.",
    )

    # --------------------------------------------------
    # Fields (user_account)
    # --------------------------------------------------

    user_account_email: str | None = Field(
        default=None,
        title="User Account Email",
        description="User account email address.",
    )

    client_secret_file: str | None = Field(
        default=None,
        title="Client Secret File",
        description="Path to an OAuth client secret file.",
    )

    client_secret_data: SecretStr | None = Field(
        default=None,
        title="Client Secret Data",
        description="OAuth client secret data as a JSON string.",
    )

    authorized_user_file: str | None = Field(
        default=None,
        title="Authorized User File",
        description="Path to an authorized user credentials file.",
    )

    authorized_user_data: SecretStr | None = Field(
        default=None,
        title="Authorized User Data",
        description="Authorized user credentials as a JSON string.",
    )

    # --------------------------------------------------
    # Fields (api_key)
    # --------------------------------------------------

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="API key for Google APIs.",
    )

    # --------------------------------------------------
    # Fields (google-genai)
    # --------------------------------------------------

    vertexai: bool | None = Field(
        default=None,
        title="Vertex AI",
        description="Whether Google Gen AI clients use Vertex AI.",
    )

    location: str | None = Field(
        default=None,
        title="Location",
        description="Google Cloud location for Google Gen AI Vertex AI clients.",
    )

    # --------------------------------------------------
    # Validators
    # --------------------------------------------------

    @field_validator(
        "service_account_file",
        "client_secret_file",
        "authorized_user_file",
        mode="before",
    )
    @classmethod
    def expand_user(cls, v: str | None) -> str | None:
        return os.path.expanduser(v) if isinstance(v, str) else v

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    def get_service_account_data(self) -> dict[str, Any] | None:
        if not self.service_account_data:
            return None

        return json.loads(self.service_account_data.get_secret_value())  # type: ignore[no-any-return]

    def get_client_secret_data(self) -> dict[str, Any] | None:
        if not self.client_secret_data:
            return None

        return json.loads(self.client_secret_data.get_secret_value())  # type: ignore[no-any-return]

    def get_authorized_user_data(self) -> dict[str, Any] | None:
        if not self.authorized_user_data:
            return None

        return json.loads(self.authorized_user_data.get_secret_value())  # type: ignore[no-any-return]


settings_manager = SettingsManager(GoogleSettings, multi=True)
"""Manager for named Google authentication settings."""
