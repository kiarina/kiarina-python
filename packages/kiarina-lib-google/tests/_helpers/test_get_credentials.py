import os

import google.auth.compute_engine.credentials
import google.oauth2.credentials
import google.oauth2.service_account
import pytest
from google.auth import impersonated_credentials

from kiarina.lib.google import GoogleSettings, get_credentials


@pytest.mark.xfail(
    not os.path.exists(
        os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    ),
    reason="ADC file not set",
)
def test_default(load_settings):
    credentials = get_credentials("default")
    assert isinstance(
        credentials,
        (
            google.auth.compute_engine.credentials.Credentials,
            google.oauth2.service_account.Credentials,
            google.oauth2.credentials.Credentials,
        ),
    )


def test_service_account_file(load_settings):
    credentials = get_credentials("service_account_file")
    assert isinstance(credentials, google.oauth2.service_account.Credentials)


def test_service_account_data(load_settings):
    credentials = get_credentials("service_account_data")
    assert isinstance(credentials, google.oauth2.service_account.Credentials)


def test_impersonate_service_account(load_settings):
    credentials = get_credentials("service_account_impersonate")
    assert isinstance(credentials, impersonated_credentials.Credentials)


def test_user_account_file(load_settings):
    credentials = get_credentials("user_account_file")
    assert isinstance(credentials, google.oauth2.credentials.Credentials)


def test_user_account_data(load_settings):
    credentials = get_credentials("user_account_data")
    assert isinstance(credentials, google.oauth2.credentials.Credentials)


def test_impersonation_requires_scopes():
    settings = GoogleSettings(
        impersonate_service_account="target@project.iam.gserviceaccount.com"
    )

    with pytest.raises(
        ValueError,
        match="Scopes are required for service account impersonation",
    ):
        get_credentials(settings=settings)
