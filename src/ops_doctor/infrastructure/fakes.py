"""In-memory fakes for tests."""

from __future__ import annotations

from ops_doctor.entities.host import HostSample, ShapeFinding


class FakeSampler:
    def __init__(self, sample: HostSample) -> None:
        self._sample = sample

    def sample(self) -> HostSample:
        return self._sample


class MemoryStore:
    def __init__(self) -> None:
        self._rows: list[HostSample] = []

    def append(self, sample: HostSample) -> None:
        self._rows.append(sample)

    def recent(self, limit: int) -> tuple[HostSample, ...]:
        return tuple(self._rows[-limit:]) if limit > 0 else ()

    def count(self) -> int:
        return len(self._rows)

    def seed(self, rows: list[HostSample]) -> None:
        self._rows.extend(rows)


class FakeShapes:
    def __init__(self, weird: bool = False, distance: float = 0.0) -> None:
        self._weird = weird
        self._distance = distance

    def find_weird(
        self, metric: str, values: tuple[float, ...], window: int, min_distance: float
    ) -> ShapeFinding:
        return ShapeFinding(
            metric=metric,
            weird=self._weird,
            distance=self._distance,
            start_index=0,
            explanation="fake",
        )
