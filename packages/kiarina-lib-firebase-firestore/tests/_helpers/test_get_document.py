from datetime import datetime

import pytest

from kiarina.lib.firebase_firestore import get_document


async def test_unauthorized(
    seed_documents: None, project_id: str, id_token: str
) -> None:
    with pytest.raises(Exception, match="403"):
        await get_document(project_id, "users/other_user/posts/hello", id_token)


async def test_happy_path(
    seed_documents: None, project_id: str, user_id: str, id_token: str
) -> None:
    snapshot = await get_document(project_id, f"users/{user_id}/posts/hello", id_token)

    assert snapshot is not None
    assert snapshot.fields.get("content") == "hello"
    assert snapshot.path == f"users/{user_id}/posts/hello"
    assert snapshot.id == "hello"
    assert isinstance(snapshot.create_time, datetime)
    assert isinstance(snapshot.update_time, datetime)


async def test_not_found(
    seed_documents: None, project_id: str, user_id: str, id_token: str
) -> None:
    snapshot = await get_document(
        project_id, f"users/{user_id}/posts/missing", id_token
    )
    assert snapshot is None
