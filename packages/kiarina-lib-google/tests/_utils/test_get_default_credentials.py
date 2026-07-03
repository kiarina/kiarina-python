import os
from typing import Any

import google.oauth2.credentials
import google.oauth2.service_account
import pytest

from kiarina.lib.google import settings_manager
from kiarina.lib.google._utils.get_default_credentials import (
    get_default_credentials,
)


@pytest.mark.xfail(
    not os.path.exists(
        os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    ),
    reason="ADC file not set",
)
def test_adc() -> None:
    credentials = get_default_credentials()
    print(f"Obtained credentials of type: {type(credentials)}")
    assert isinstance(credentials, google.oauth2.credentials.Credentials)


def test_service_account(load_settings: Any, monkeypatch: Any) -> None:
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        settings = settings_manager.get_settings("service_account_file")
        monkeypatch.setenv(
            "GOOGLE_APPLICATION_CREDENTIALS", settings.service_account_file
        )

    credentials = get_default_credentials()
    print(f"Obtained service account credentials of type: {type(credentials)}")
    assert isinstance(credentials, google.oauth2.service_account.Credentials)
