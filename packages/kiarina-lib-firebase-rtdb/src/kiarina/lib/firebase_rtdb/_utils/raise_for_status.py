from typing import Literal

import httpx

type Operation = Literal["get", "update", "watch"]

_ERROR_TYPES = {
    1: "Informational response",
    3: "Redirect response",
    4: "Client error",
    5: "Server error",
}


async def raise_for_status(response: httpx.Response, *, operation: Operation) -> None:
    # httpx's own error puts the request URL, and with it the ID token in the
    # auth query parameter, into the message and the attached request.
    if response.is_success:
        return

    try:
        content = await response.aread()
    except httpx.HTTPError:
        content = b""

    # Built outside an except block so the error has no chained exception
    # that still references the token.
    request = httpx.Request(
        response.request.method,
        response.request.url.copy_remove_param("auth"),
        headers=response.request.headers,
    )
    redacted = httpx.Response(
        response.status_code,
        headers=[
            (name, value)
            for name, value in response.headers.multi_items()
            if name.lower() != "content-encoding"
        ],
        content=content,
        request=request,
    )

    error_type = _ERROR_TYPES.get(response.status_code // 100, "Invalid status code")
    raise httpx.HTTPStatusError(
        f"RTDB {operation} failed: {error_type} "
        f"'{response.status_code} {response.reason_phrase}' for url '{request.url}'",
        request=request,
        response=redacted,
    )
