import httpx

from .._operations.resolve_id_token import resolve_id_token
from .._schemas.document_list import DocumentList
from .._settings import settings_manager
from .._utils.parse_document import parse_document


async def list_documents(
    project_id: str,
    collection_path: str,
    *,
    database_id: str = "(default)",
    page_size: int | None = None,
    page_token: str | None = None,
    order_by: str | None = None,
    id_token: str | None = None,
) -> DocumentList:
    settings = settings_manager.get_settings()

    url = (
        f"{settings.base_url.rstrip('/')}/v1/projects/{project_id}"
        f"/databases/{database_id}/documents/{collection_path.strip('/')}"
    )
    headers = {"Authorization": f"Bearer {await resolve_id_token(id_token)}"}

    params: dict[str, int | str] = {}

    if page_size is not None:
        params["pageSize"] = page_size

    if page_token is not None:
        params["pageToken"] = page_token

    if order_by is not None:
        params["orderBy"] = order_by

    async with httpx.AsyncClient(
        timeout=settings.timeout, follow_redirects=True
    ) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    return DocumentList(
        documents=[parse_document(doc) for doc in data.get("documents", [])],
        next_page_token=data.get("nextPageToken"),
    )
