from datetime import UTC

import pytest

from kiarina.agi.memory import Memory
from kiarina.agi.memory_graph import MemoryGraph


@pytest.fixture
def graph() -> MemoryGraph:
    return MemoryGraph()


def create_memory(id: str, *, memory_type: str = "concept") -> Memory:
    return Memory(id=id, type=memory_type)


def test_clear(graph: MemoryGraph) -> None:
    graph.mset([create_memory("m1"), create_memory("m2")])
    graph.connect("m1", "m2")

    graph.clear()

    assert graph.count() == 0
    assert graph.edges == {}


def test_get_and_set(graph: MemoryGraph) -> None:
    memory = create_memory("m1")

    graph.set(memory)

    assert graph.count() == 1
    assert graph.get("m1") == memory
    assert graph.get("missing") is None


def test_mget_and_mset(graph: MemoryGraph) -> None:
    memories = [create_memory("m1"), create_memory("m2")]

    graph.mset(memories)

    assert graph.mget(["m2", "missing", "m1"]) == [memories[1], memories[0]]


def test_delete_removes_node_and_all_connected_edges(graph: MemoryGraph) -> None:
    graph.mset([create_memory("m1"), create_memory("m2"), create_memory("m3")])
    graph.connect("m1", "m2")
    graph.connect("m3", "m1", bidirectional=False)

    graph.delete("m1")

    assert graph.get("m1") is None
    assert graph.edges == {}


def test_connect_is_bidirectional_by_default(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("time.time", lambda: 100.0)

    graph.connect("m1", "m2", remaining_time=10)

    assert graph.edges == {"m1": {"m2": 110.0}, "m2": {"m1": 110.0}}


def test_connect_can_be_unidirectional(graph: MemoryGraph) -> None:
    graph.connect("m1", "m2", bidirectional=False)

    assert graph.edges == {"m1": {"m2": 0}}


def test_connect_promotes_an_existing_edge_to_permanent(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("time.time", lambda: 100.0)
    graph.connect("m1", "m2", remaining_time=10)

    graph.connect("m1", "m2")

    assert graph.edges["m1"]["m2"] == 0
    assert graph.edges["m2"]["m1"] == 0


def test_connect_extends_an_existing_decaying_edge(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    now = 100.0
    monkeypatch.setattr("time.time", lambda: now)
    graph.connect("m1", "m2", remaining_time=10)

    now = 105.0
    graph.connect("m1", "m2", remaining_time=10)

    assert graph.edges["m1"]["m2"] == 120.0
    assert graph.edges["m2"]["m1"] == 120.0


def test_connect_does_not_change_a_permanent_edge(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    graph.connect("m1", "m2")
    monkeypatch.setattr("time.time", lambda: 100.0)

    graph.connect("m1", "m2", remaining_time=10)

    assert graph.edges["m1"]["m2"] == 0
    assert graph.edges["m2"]["m1"] == 0


def test_disconnect_removes_empty_edge_groups(graph: MemoryGraph) -> None:
    graph.connect("m1", "m2")

    graph.disconnect("m1", "m2")

    assert graph.edges == {}


def test_disconnect_can_be_unidirectional(graph: MemoryGraph) -> None:
    graph.connect("m1", "m2")

    graph.disconnect("m1", "m2", bidirectional=False)

    assert graph.edges == {"m2": {"m1": 0}}


def test_forget_accelerates_decay(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("time.time", lambda: 100.0)
    graph.connect("m1", "m2", remaining_time=20)

    graph.forget("m1", "m2", acceleration_time=5)

    assert graph.edges["m1"]["m2"] == 115.0
    assert graph.edges["m2"]["m1"] == 115.0


def test_forget_removes_an_expired_edge(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("time.time", lambda: 100.0)
    graph.connect("m1", "m2", remaining_time=10)

    graph.forget("m1", "m2", acceleration_time=10)

    assert graph.edges == {}


def test_forget_does_not_change_a_permanent_edge(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    graph.connect("m1", "m2")
    monkeypatch.setattr("time.time", lambda: 100.0)

    graph.forget("m1", "m2", acceleration_time=10)

    assert graph.edges == {"m1": {"m2": 0}, "m2": {"m1": 0}}


def test_find_adjacent_ids_honors_depth_and_ignores_missing_nodes(
    graph: MemoryGraph,
) -> None:
    graph.mset([create_memory("m1"), create_memory("m2"), create_memory("m3")])
    graph.connect("m1", "m2")
    graph.connect("m2", "m3")
    graph.connect("m1", "missing", bidirectional=False)

    assert graph.find_adjacent_ids("m1", depth=1) == ["m2"]
    assert graph.find_adjacent_ids("m1", depth=2) == ["m2", "m3"]


def test_find_adjacent_ids_filters_memory_type(graph: MemoryGraph) -> None:
    graph.mset(
        [
            create_memory("m1"),
            create_memory("m2", memory_type="entity"),
            create_memory("m3", memory_type="concept"),
        ]
    )
    graph.connect("m1", "m2")
    graph.connect("m1", "m3")

    assert graph.find_adjacent_ids("m1", memory_type="entity") == ["m2"]


def test_find_adjacent_ids_excludes_expired_edges(
    graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    graph.mset([create_memory("m1"), create_memory("m2"), create_memory("m3")])
    now = 100.0
    monkeypatch.setattr("time.time", lambda: now)
    graph.connect("m1", "m2", remaining_time=10)
    graph.connect("m1", "m3")

    now = 110.0

    assert graph.find_adjacent_ids("m1") == ["m3"]


def test_find_adjacent_ids_sorts_by_active_edge_count_then_id(
    graph: MemoryGraph,
) -> None:
    graph.mset(
        [
            create_memory("root"),
            create_memory("a"),
            create_memory("b"),
            create_memory("c"),
        ]
    )
    graph.connect("root", "a")
    graph.connect("root", "b")
    graph.connect("a", "c")

    assert graph.find_adjacent_ids("root") == ["a", "b"]


def test_find_adjacent_ids_applies_offset_and_limit(graph: MemoryGraph) -> None:
    graph.mset(
        [
            create_memory("root"),
            create_memory("a"),
            create_memory("b"),
            create_memory("c"),
        ]
    )
    graph.connect("root", "a")
    graph.connect("root", "b")
    graph.connect("root", "c")

    assert graph.find_adjacent_ids("root", offset=1, limit=1) == ["b"]


def test_model_dump_and_validate_restore_the_graph() -> None:
    graph = MemoryGraph()
    graph.mset([create_memory("m1"), create_memory("m2")])
    graph.connect("m1", "m2", remaining_time=10)

    restored = MemoryGraph.model_validate(graph.model_dump(mode="json"))

    assert restored == graph


def test_find_ids_orders_by_activation_then_id_and_pages_after_type_filter(
    graph: MemoryGraph,
) -> None:
    from datetime import datetime

    old = datetime(2026, 1, 1, tzinfo=UTC)
    recent = datetime(2026, 2, 1, tzinfo=UTC)
    graph.mset(
        [
            Memory(id="z", type="episode", activated_at=old),
            Memory(id="b", type="episode", activated_at=recent),
            Memory(id="a", type="episode", activated_at=recent),
            Memory(id="c", type="identity", activated_at=recent),
        ]
    )
    before = graph.model_dump_json()
    assert graph.find_ids() == ["a", "b", "c", "z"]
    assert graph.find_ids(memory_type="episode") == ["a", "b", "z"]
    assert graph.find_ids(memory_type="episode", offset=1, limit=1) == ["b"]
    assert graph.find_ids(memory_type="episode", offset=1) == ["b", "z"]
    assert graph.find_ids(offset=20) == []
    assert graph.find_ids(memory_type="absent") == []
    assert graph.model_dump_json() == before
    graph.nodes["z"].activated_at = datetime(2026, 3, 1, tzinfo=UTC)
    assert graph.find_ids()[0] == "z"


@pytest.fixture
def vector_graph() -> MemoryGraph:
    graph = MemoryGraph()
    graph.mset(
        [
            Memory(id="b", type="episode", vector=[2.0, 0.0]),
            Memory(id="a", type="episode", vector=[1.0, 0.0]),
            Memory(id="d", type="identity", vector=[1.0, 1.0]),
            Memory(id="c", type="episode", vector=[0.0, 1.0]),
            Memory(id="e", type="episode", vector=[-1.0, 0.0]),
            Memory(id="no-vector", type="episode"),
            Memory(id="empty-vector", type="episode", vector=[]),
        ]
    )
    return graph


def test_search_ids_ranks_cosine_with_stable_ties_and_no_mutation(
    vector_graph: MemoryGraph,
) -> None:
    before = vector_graph.model_dump_json()
    assert vector_graph.search_ids([1.0, 0.0]) == ["a", "b", "d"]
    assert vector_graph.search_ids([1.0, 0.0], k=20) == ["a", "b", "d", "c", "e"]
    assert vector_graph.search_ids([1.0, 0.0], k=20, min_score=0) == [
        "a",
        "b",
        "d",
        "c",
    ]
    assert vector_graph.search_ids([1.0, 0.0], min_score=1) == ["a", "b"]
    assert vector_graph.search_ids([1.0, 0.0], memory_type="identity") == ["d"]
    assert vector_graph.model_dump_json() == before


def test_search_ids_intersects_type_and_ids_before_top_k(
    vector_graph: MemoryGraph,
) -> None:
    assert vector_graph.search_ids(
        [1.0, 0.0], ids=["c", "d", "e"], memory_type="episode", k=1
    ) == ["c"]
    assert vector_graph.search_ids([1.0, 0.0], ids=["b", "a", "b", "missing"]) == [
        "a",
        "b",
    ]
    assert vector_graph.search_ids([1.0, 0.0], ids=[]) == []
    assert vector_graph.search_ids([1.0, 0.0], ids=["missing"]) == []
    assert vector_graph.search_ids([1.0, 0.0], ids=["no-vector", "empty-vector"]) == []
    assert vector_graph.search_ids([1.0, 0.0], memory_type="absent") == []
    assert MemoryGraph().search_ids([1.0, 0.0]) == []


def test_adjacent_ids_feed_search_without_expanding_empty_scope(
    vector_graph: MemoryGraph, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("time.time", lambda: 100.0)
    vector_graph.connect("emotion", "c", bidirectional=False)
    vector_graph.connect("emotion", "e", bidirectional=False)
    vector_graph.edges["emotion"]["a"] = 99.0
    assert vector_graph.search_ids(
        [1.0, 0.0], ids=vector_graph.find_adjacent_ids("emotion"), k=1
    ) == ["c"]
    assert (
        vector_graph.search_ids(
            [1.0, 0.0], ids=vector_graph.find_adjacent_ids("unknown")
        )
        == []
    )


@pytest.mark.parametrize(
    "query", [[], [0.0, 0.0], [float("nan"), 0.0], [float("inf"), 0.0]]
)
def test_search_ids_rejects_invalid_query(
    vector_graph: MemoryGraph, query: list[float]
) -> None:
    with pytest.raises(ValueError, match="query_vector"):
        vector_graph.search_ids(query)


@pytest.mark.parametrize(
    "vector", [[1.0], [0.0, 0.0], [float("nan"), 0.0], [float("inf"), 0.0]]
)
def test_search_ids_validates_only_selected_candidate_vectors(
    vector_graph: MemoryGraph, vector: list[float]
) -> None:
    vector_graph.set(Memory(id="invalid", type="invalid", vector=vector))
    assert vector_graph.search_ids([1.0, 0.0], memory_type="episode", k=1) == ["a"]
    assert vector_graph.search_ids([1.0, 0.0], ids=["a"], k=1) == ["a"]
    with pytest.raises(ValueError, match="invalid"):
        vector_graph.search_ids([1.0, 0.0], ids=["invalid"])


@pytest.mark.parametrize("offset,limit", [(-1, 0), (0, -1)])
def test_find_ids_rejects_negative_pagination(
    graph: MemoryGraph, offset: int, limit: int
) -> None:
    with pytest.raises(ValueError):
        graph.find_ids(offset=offset, limit=limit)


@pytest.mark.parametrize("k", [0, -1])
def test_search_ids_rejects_nonpositive_k(graph: MemoryGraph, k: int) -> None:
    with pytest.raises(ValueError, match="k"):
        graph.search_ids([1.0], k=k)


@pytest.mark.parametrize("min_score", [-1.1, 1.1, float("nan")])
def test_search_ids_rejects_invalid_threshold(
    graph: MemoryGraph, min_score: float
) -> None:
    with pytest.raises(ValueError, match="min_score"):
        graph.search_ids([1.0], min_score=min_score)
