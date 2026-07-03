from typing import Any

import pytest

import kiarina.utils.file as kf
from kiarina.lib.redisearch.asyncio import RedisearchClient


@pytest.fixture
def fields() -> Any:
    return [
        {"type": "tag", "name": "id"},
        {"type": "text", "name": "title"},
        {"type": "vector", "name": "embedding", "algorithm": "FLAT", "dims": 3072},
    ]


@pytest.fixture
def data_rows(assets_dir: Any) -> Any:
    return kf.read_json_list(
        assets_dir / "json" / "id_title_content_embedding_3row_apple_car_dog.json"
    )


@pytest.fixture
def data_query(assets_dir: Any) -> Any:
    return kf.read_json_dict(
        assets_dir / "json" / "query_embedding_tell_me_about_dogs_not_apples.json"
    )


async def test_search(
    client: RedisearchClient, data_rows: Any, data_query: Any
) -> None:
    await client.reset_index()

    for row in data_rows:
        await client.set(row)

    # The simplest search
    result = await client.search(
        vector=data_query["embedding"],
    )

    assert result.total == 3
    assert all(doc.id in ("1", "2", "3") for doc in result.documents)
    assert result.documents[0].id == "3"
    assert result.documents[1].id == "1"
    assert result.documents[2].id == "2"

    # Return the id field included in the document's mapping
    result = await client.search(
        vector=data_query["embedding"],
        return_fields=["id"],
    )

    assert result.total == 3
    assert "id" in result.documents[0].mapping
    assert ":" not in result.documents[0].mapping["id"]

    # After narrowing down the parent set, perform vector search
    result = await client.search(
        vector=data_query["embedding"],
        filter=[
            ["id", "in", ("1", "3")],
        ],
    )

    assert result.total == 2
    assert all(doc.id in ("1", "3") for doc in result.documents)

    # Offset and limit
    result = await client.search(
        vector=data_query["embedding"],
        offset=1,
        limit=2,
    )

    assert result.total == 2
    assert len(result.documents) == 1
    assert result.documents[0].id == "1"
