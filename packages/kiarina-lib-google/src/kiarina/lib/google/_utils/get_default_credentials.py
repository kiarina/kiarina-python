import google.auth.compute_engine.credentials
import google.oauth2.credentials
import google.oauth2.service_account
from google.auth import default


def get_default_credentials() -> (
    google.auth.compute_engine.credentials.Credentials
    | google.oauth2.credentials.Credentials
    | google.oauth2.service_account.Credentials
):
    credentials, _ = default()

    assert isinstance(
        credentials,
        (
            google.auth.compute_engine.credentials.Credentials,
            google.oauth2.credentials.Credentials,
            google.oauth2.service_account.Credentials,
        ),
    ), f"Invalid credentials type: {type(credentials)}"

    return credentials
