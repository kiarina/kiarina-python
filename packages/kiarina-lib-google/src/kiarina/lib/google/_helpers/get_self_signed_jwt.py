from google.auth import jwt
from google.auth.transport.requests import Request

from .._settings import GoogleSettings
from .._types.self_signed_jwt import SelfSignedJWT
from .get_credentials import get_credentials


def get_self_signed_jwt(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    audience: str,
) -> SelfSignedJWT:
    credentials = get_credentials(settings_key, settings=settings)

    jwt_creds = jwt.Credentials.from_signing_credentials(credentials, audience=audience)  # type: ignore[no-untyped-call]
    # Generate a self-signed JWT. Does not communicate over the network
    jwt_creds.refresh(Request())

    return jwt_creds.token.decode("utf-8")  # type: ignore[no-any-return]
