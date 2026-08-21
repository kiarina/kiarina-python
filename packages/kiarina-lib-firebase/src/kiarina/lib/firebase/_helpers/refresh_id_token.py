import httpx

from .._exceptions.firebase_api_error import FirebaseAPIError
from .._exceptions.invalid_refresh_token_error import InvalidRefreshTokenError
from .._schemas.token import Token


async def refresh_id_token(token: Token, api_key: str) -> Token:
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.content else {}
            error_message = error_data.get("error", {}).get("message", str(e))
            error_code = error_data.get("error", {}).get("code")

            if (
                "INVALID_REFRESH_TOKEN" in error_message
                or "TOKEN_EXPIRED" in error_message
            ):
                raise InvalidRefreshTokenError(
                    f"Invalid or expired refresh token: {error_message}"
                ) from e

            raise FirebaseAPIError(
                message=f"Firebase API error: {error_message}",
                status_code=e.response.status_code,
                error_code=error_code,
            ) from e

        except httpx.RequestError as e:
            raise FirebaseAPIError(f"Request failed: {e}") from e

    data = response.json()

    return Token(
        id_token=data["id_token"],
        refresh_token=data["refresh_token"],
    )
