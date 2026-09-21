"""Ports for sampling, persistence, and shape analysis."""

from __future__ import annotations

from typing import Protocol

from ops_doctor.entities.host import HostSample, ShapeFinding


class HostSampler(Protocol):
    def sample(self) -> HostSample: ...


class SampleStore(Protocol):
    def append(self, sample: HostSample) -> None: ...

    def recent(self, limit: int) -> tuple[HostSample, ...]: ...

    def count(self) -> int: ...


class ShapeAnalyzer(Protocol):
    def find_weird(
        self, metric: str, values: tuple[float, ...], window: int, min_distance: float
    ) -> ShapeFinding: ...
