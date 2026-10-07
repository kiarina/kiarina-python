from typing import Any

from .._settings import AnthropicVertexChatProviderSettings

try:
    import google.auth
    from anthropic import AsyncAnthropicVertex

    import kiarina.lib.google
    from kiarina.agi.chat_provider_impl.anthropic import AnthropicChatProvider
except ImportError as exc:
    raise ImportError(
        "anthropic[vertex], kiarina-lib-anthropic, and kiarina-lib-google are "
        "required to use AnthropicVertexChatProvider. "
        "Install them with: pip install "
        "'kiarina-agi-text[chat-provider-anthropic-vertex]'"
    ) from exc


class AnthropicVertexChatProvider(AnthropicChatProvider):
    """
    Anthropic Vertex Chat Provider Implementation

    Calls Claude on Vertex AI with the Anthropic SDK. Token counting also goes
    through Vertex AI, so no Anthropic API key is needed.
    """

    def __init__(self, settings: AnthropicVertexChatProviderSettings) -> None:
        super().__init__(settings)

        self.settings: AnthropicVertexChatProviderSettings = settings

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def google_auth_settings(self) -> kiarina.lib.google.GoogleSettings:
        return kiarina.lib.google.settings_manager.get_settings(
            self.settings.google_auth_settings_key
        )

    # --------------------------------------------------
    # Protected Methods
    # --------------------------------------------------

    def _create_client(self) -> Any:
        client_kwargs: dict[str, Any] = kiarina.lib.google.get_cloud_options(
            settings=self.google_auth_settings,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        if project_id := self._resolve_project_id(client_kwargs.get("credentials")):
            client_kwargs["project_id"] = project_id

        return AsyncAnthropicVertex(
            region=self.settings.vertex_ai_location,
            timeout=self.settings.timeout,
            max_retries=self.settings.max_retry_count,
            **client_kwargs,
        )

    def _resolve_project_id(self, credentials: Any) -> str | None:
        """
        The SDK needs the project up front. Fall back to the default credentials
        and `GOOGLE_CLOUD_PROJECT`, as `ChatAnthropicVertex` does.
        """
        if project_id := self.google_auth_settings.project_id:
            return project_id

        if project_id := getattr(credentials, "project_id", None):
            return str(project_id)

        try:
            _, project_id = google.auth.default()
        except Exception:
            return None

        return project_id or None
