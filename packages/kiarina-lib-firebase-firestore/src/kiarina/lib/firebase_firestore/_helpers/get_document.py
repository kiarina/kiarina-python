import httpx

from kiarina.lib.firebase import Token

from .._operations.resolve_token import resolve_token
from .._schemas.document_snapshot import DocumentSnapshot
from .._settings import settings_manager
from .._utils.parse_document import parse_document


async def get_document(
    path: str,
    *,
    project_id: str | None = None,
    database_id: str = "(default)",
    token: Token | None = None,
) -> DocumentSnapshot | None:
    settings = settings_manager.get_settings()
    token = await resolve_token(token)

    url = (
        f"{settings.base_url.rstrip('/')}/v1/projects/{project_id or token.project_id}"
        f"/databases/{database_id}/documents/{path.strip('/')}"
    )
    headers = {"Authorization": f"Bearer {token.id_token}"}

    async with httpx.AsyncClient(
        timeout=settings.timeout, follow_redirects=True
    ) as client:
        response = await client.get(url, headers=headers)

        if response.status_code == httpx.codes.NOT_FOUND:
            return None

        response.raise_for_status()
        return parse_document(response.json())
