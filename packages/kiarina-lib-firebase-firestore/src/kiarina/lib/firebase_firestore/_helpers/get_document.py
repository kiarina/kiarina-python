import httpx

from .._operations.resolve_id_token import resolve_id_token
from .._schemas.document_snapshot import DocumentSnapshot
from .._settings import settings_manager
from .._utils.parse_document import parse_document


async def get_document(
    project_id: str,
    path: str,
    *,
    database_id: str = "(default)",
    id_token: str | None = None,
) -> DocumentSnapshot | None:
    settings = settings_manager.get_settings()

    url = (
        f"{settings.base_url.rstrip('/')}/v1/projects/{project_id}"
        f"/databases/{database_id}/documents/{path.strip('/')}"
    )
    headers = {"Authorization": f"Bearer {await resolve_id_token(id_token)}"}

    async with httpx.AsyncClient(
        timeout=settings.timeout, follow_redirects=True
    ) as client:
        response = await client.get(url, headers=headers)

        if response.status_code == httpx.codes.NOT_FOUND:
            return None

        response.raise_for_status()
        return parse_document(response.json())
