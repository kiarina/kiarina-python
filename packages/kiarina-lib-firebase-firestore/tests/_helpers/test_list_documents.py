from kiarina.lib.firebase_firestore import list_documents


async def test_happy_path(
    seed_documents: None, project_id: str, user_id: str, id_token: str
) -> None:
    result = await list_documents(project_id, f"users/{user_id}/items", id_token)

    assert [doc.id for doc in result.documents] == ["a", "b", "c"]
    assert result.documents[0].fields.get("label") == "a"
    assert result.next_page_token is None


async def test_pagination(
    seed_documents: None, project_id: str, user_id: str, id_token: str
) -> None:
    first_page = await list_documents(
        project_id, f"users/{user_id}/items", id_token, page_size=2
    )

    assert len(first_page.documents) == 2
    assert first_page.next_page_token is not None

    second_page = await list_documents(
        project_id,
        f"users/{user_id}/items",
        id_token,
        page_size=2,
        page_token=first_page.next_page_token,
    )

    assert [doc.id for doc in second_page.documents] == ["c"]


async def test_empty_collection(
    seed_documents: None, project_id: str, user_id: str, id_token: str
) -> None:
    result = await list_documents(project_id, f"users/{user_id}/empty", id_token)

    assert result.documents == []
    assert result.next_page_token is None
