import time

from pydantic import BaseModel, Field

from kiarina.agi.memory import Memory, MemoryID, MemoryType

from .._types.decay_time import DecayTime


class MemoryGraph(BaseModel):
    nodes: dict[MemoryID, Memory] = Field(default_factory=dict)
    edges: dict[MemoryID, dict[MemoryID, DecayTime]] = Field(default_factory=dict)

    def clear(self) -> None:
        self.nodes.clear()
        self.edges.clear()

    def count(self) -> int:
        return len(self.nodes)

    def get(self, id: MemoryID) -> Memory | None:
        return self.nodes.get(id)

    def mget(self, ids: list[MemoryID]) -> list[Memory]:
        return [self.nodes[id] for id in ids if id in self.nodes]

    def set(self, memory: Memory) -> None:
        self.nodes[memory.id] = memory

    def mset(self, memories: list[Memory]) -> None:
        for memory in memories:
            self.set(memory)

    def delete(self, id: MemoryID) -> None:
        self.edges.pop(id, None)

        empty_source_ids: list[MemoryID] = []

        for source_id, targets in self.edges.items():
            targets.pop(id, None)

            if not targets:
                empty_source_ids.append(source_id)

        for source_id in empty_source_ids:
            del self.edges[source_id]

        self.nodes.pop(id, None)

    def connect(
        self,
        source_id: MemoryID,
        target_id: MemoryID,
        *,
        bidirectional: bool = True,
        remaining_time: float = 0,
    ) -> None:
        now = time.time()
        self._connect(source_id, target_id, remaining_time, now)

        if bidirectional:
            self._connect(target_id, source_id, remaining_time, now)

    def disconnect(
        self,
        source_id: MemoryID,
        target_id: MemoryID,
        *,
        bidirectional: bool = True,
    ) -> None:
        self._disconnect(source_id, target_id)

        if bidirectional:
            self._disconnect(target_id, source_id)

    def forget(
        self,
        source_id: MemoryID,
        target_id: MemoryID,
        *,
        bidirectional: bool = True,
        acceleration_time: float = 0,
    ) -> None:
        now = time.time()
        self._forget(source_id, target_id, acceleration_time, now)

        if bidirectional:
            self._forget(target_id, source_id, acceleration_time, now)

    def find_adjacent_ids(
        self,
        id: MemoryID,
        *,
        depth: int = 1,
        memory_type: MemoryType | None = None,
        offset: int = 0,
        limit: int = 0,
    ) -> list[MemoryID]:
        now = time.time()
        visited = {id}
        current_level = {id}

        for _ in range(depth):
            next_level: set[MemoryID] = set()

            for current_id in current_level:
                for target_id, decay_time in self.edges.get(current_id, {}).items():
                    if decay_time > 0 and decay_time <= now:
                        continue

                    if target_id in visited:
                        continue

                    memory = self.nodes.get(target_id)

                    if memory is None:
                        continue

                    if memory_type is not None and memory.type != memory_type:
                        continue

                    next_level.add(target_id)
                    visited.add(target_id)

            current_level = next_level

            if not current_level:
                break

        visited.discard(id)
        sorted_ids = sorted(
            visited,
            key=lambda memory_id: (-self._count_edges(memory_id, now), memory_id),
        )

        if limit > 0:
            return sorted_ids[offset : offset + limit]

        return sorted_ids[offset:]

    def _connect(
        self,
        source_id: MemoryID,
        target_id: MemoryID,
        remaining_time: float,
        now: float,
    ) -> None:
        targets = self.edges.setdefault(source_id, {})
        current_decay_time = targets.get(target_id)

        if current_decay_time == 0:
            return

        if remaining_time == 0:
            targets[target_id] = 0
        elif current_decay_time is None:
            targets[target_id] = now + remaining_time
        else:
            targets[target_id] = max(current_decay_time, now) + remaining_time

    def _disconnect(self, source_id: MemoryID, target_id: MemoryID) -> None:
        targets = self.edges.get(source_id)

        if targets is None:
            return

        targets.pop(target_id, None)

        if not targets:
            del self.edges[source_id]

    def _forget(
        self,
        source_id: MemoryID,
        target_id: MemoryID,
        acceleration_time: float,
        now: float,
    ) -> None:
        targets = self.edges.get(source_id)

        if targets is None:
            return

        decay_time = targets.get(target_id)

        if decay_time is None or decay_time == 0:
            return

        decay_time -= acceleration_time

        if decay_time <= now:
            self._disconnect(source_id, target_id)
        else:
            targets[target_id] = decay_time

    def _count_edges(self, id: MemoryID, now: float) -> int:
        return sum(
            decay_time == 0 or decay_time > now
            for decay_time in self.edges.get(id, {}).values()
        )
