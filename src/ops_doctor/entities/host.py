"""Host sample and preflight verdict entities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    SOFT_WARN = "SOFT_WARN"
    BLOCK = "BLOCK"


@dataclass(frozen=True, slots=True)
class HostSample:
    timestamp: float
    cpu_percent: float
    ram_used_percent: float
    ram_available_mb: float
    disk_free_gb: float


@dataclass(frozen=True, slots=True)
class GateThresholds:
    min_ram_mb: float = 512.0
    min_disk_gb: float = 2.0
    max_cpu_percent: float = 92.0
    heavy_min_ram_mb: float = 1024.0
    heavy_min_disk_gb: float = 5.0
    heavy_max_cpu_percent: float = 80.0
    shape_min_points: int = 36
    shape_window: int = 12
    shape_min_distance: float = 2.0


@dataclass(frozen=True, slots=True)
class ShapeFinding:
    metric: str
    weird: bool
    distance: float
    start_index: int
    explanation: str


@dataclass(frozen=True, slots=True)
class PreflightReport:
    verdict: Verdict
    sample: HostSample
    reasons: tuple[str, ...]
    shapes: tuple[ShapeFinding, ...]
    history_points: int
