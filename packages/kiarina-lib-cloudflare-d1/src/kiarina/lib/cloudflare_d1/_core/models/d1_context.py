from dataclasses import dataclass

from kiarina.lib.cloudflare import CloudflareSettings

from ..._settings import D1Settings


@dataclass
class D1Context:
    settings: D1Settings

    auth_settings: CloudflareSettings

    @property
    def query_api_url(self) -> str:
        return f"https://api.cloudflare.com/client/v4/accounts/{self.auth_settings.account_id}/d1/database/{self.settings.database_id}/query"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.auth_settings.api_token.get_secret_value()}",
            "Content-Type": "application/json",
        }
