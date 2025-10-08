import json
import os

from google.oauth2.credentials import Credentials
import pytest

from kiarina.lib.google.auth import CredentialsCache, get_user_account_credentials


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_FILE" not in os.environ,
    reason="GCP authorized user file not set",
)
def test_file():
    credentials = get_user_account_credentials(
        authorized_user_file=os.environ[
            "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_FILE"
        ],
        scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
    )
    assert isinstance(credentials, Credentials)


def test_nonexistent_file():
    with pytest.raises(ValueError, match="Authorized user file does not exist"):
        get_user_account_credentials(
            authorized_user_file="/path/to/nonexistent/file.json",
            scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
        )


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA" not in os.environ,
    reason="GCP authorized user data not set",
)
def test_data():
    credentials = get_user_account_credentials(
        authorized_user_data=json.loads(
            os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA"]
        ),
        scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
    )
    assert isinstance(credentials, Credentials)


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA" not in os.environ,
    reason="GCP authorized user data not set",
)
def test_cache():
    class InMemoryCache(CredentialsCache):
        def __init__(self):
            self._credentials = None

        def get(self) -> Credentials | None:
            return self._credentials

        def set(self, credentials: Credentials) -> None:
            self._credentials = credentials

    credentials = get_user_account_credentials(
        authorized_user_data=json.loads(
            os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA"]
        ),
        scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
        cache=InMemoryCache(),
    )
    assert isinstance(credentials, Credentials)
