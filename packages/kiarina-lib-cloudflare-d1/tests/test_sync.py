import os

import pytest

from kiarina.lib.cloudflare.auth import CloudflareAuthSettings
from kiarina.lib.cloudflare.d1 import D1Client, D1Settings, create_d1_client


@pytest.mark.xfail(
    "KIARINA_LIB_CLOUDFLARE_AUTH_TEST_ACCOUNT_ID" not in os.environ or
    "KIARINA_LIB_CLOUDFLARE_AUTH_TEST_API_TOKEN" not in os.environ or
    "KIARINA_LIB_CLOUDFLARE_D1_TEST_DATABASE_ID" not in os.environ,
    reason="Cloudflare D1 test settings not set",
)
def test_create_d1_client() -> None:
    auth_settings = CloudflareAuthSettings.model_validate(
        {
            "account_id": os.environ["KIARINA_LIB_CLOUDFLARE_AUTH_TEST_ACCOUNT_ID"],
            "api_token": os.environ["KIARINA_LIB_CLOUDFLARE_AUTH_TEST_API_TOKEN"],
        }
    )

    settings = D1Settings(
        database_id=os.environ["KIARINA_LIB_CLOUDFLARE_D1_TEST_DATABASE_ID"],
    )

    # TODO: Mock
    # client = create_d1_client()
