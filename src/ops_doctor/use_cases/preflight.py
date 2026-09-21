"""Use case: record a sample and evaluate hard+soft host preflight."""

from __future__ import annotations

from dataclasses import dataclass

from ops_doctor.entities.host import (
    GateThresholds,
    HostSample,
    PreflightReport,
    ShapeFinding,
    Verdict,
)
from ops_doctor.interfaces.ports import HostSampler, SampleStore, ShapeAnalyzer


@dataclass(frozen=True, slots=True)
class PreflightRequest:
    heavy: bool = False


class RecordAndPreflightUseCase:
    def __init__(
        self,
        sampler: HostSampler,
        store: SampleStore,
        shapes: ShapeAnalyzer,
        thresholds: GateThresholds | None = None,
    ) -> None:
        self._sampler = sampler
        self._store = store
        self._shapes = shapes
        self._thresholds = thresholds or GateThresholds()

    def execute(self, request: PreflightRequest) -> PreflightReport:
        sample = self._sampler.sample()
        self._store.append(sample)
        hard = self._hard_reasons(sample, request.heavy)
        if hard:
            return self._report(Verdict.BLOCK, sample, hard, ())
        soft, findings = self._soft_signals(sample, request.heavy)
        verdict = Verdict.SOFT_WARN if soft else Verdict.ALLOW
        return self._report(verdict, sample, soft, findings)

    def _report(
        self,
        verdict: Verdict,
        sample: HostSample,
        reasons: tuple[str, ...],
        shapes: tuple[ShapeFinding, ...],
    ) -> PreflightReport:
        return PreflightReport(verdict, sample, reasons, shapes, self._store.count())

    def _hard_reasons(self, sample: HostSample, heavy: bool) -> tuple[str, ...]:
        t = self._thresholds
        min_ram = t.heavy_min_ram_mb if heavy else t.min_ram_mb
        min_disk = t.heavy_min_disk_gb if heavy else t.min_disk_gb
        max_cpu = t.heavy_max_cpu_percent if heavy else t.max_cpu_percent
        reasons: list[str] = []
        if sample.ram_available_mb < min_ram:
            reasons.append(
                f"RAM available {sample.ram_available_mb:.0f}MB < {min_ram:.0f}MB"
            )
        if sample.disk_free_gb < min_disk:
            reasons.append(f"Disk free {sample.disk_free_gb:.1f}GB < {min_disk:.1f}GB")
        if sample.cpu_percent >= max_cpu:
            reasons.append(f"CPU {sample.cpu_percent:.0f}% >= {max_cpu:.0f}%")
        return tuple(reasons)

    def _soft_signals(
        self, sample: HostSample, heavy: bool
    ) -> tuple[tuple[str, ...], tuple[ShapeFinding, ...]]:
        t = self._thresholds
        reasons: list[str] = []
        findings: list[ShapeFinding] = []
        warn_cpu = 70.0 if heavy else 85.0
        block_cpu = t.heavy_max_cpu_percent if heavy else t.max_cpu_percent
        if warn_cpu <= sample.cpu_percent < block_cpu:
            reasons.append(f"CPU elevated at {sample.cpu_percent:.0f}%")
        findings.extend(self._shape_scan())
        for finding in findings:
            if finding.weird:
                reasons.append(
                    f"Strange {finding.metric} shape "
                    f"(discord dist={finding.distance:.2f})"
                )
        return tuple(reasons), tuple(findings)

    def _shape_scan(self) -> list[ShapeFinding]:
        t = self._thresholds
        history = self._store.recent(max(t.shape_min_points, t.shape_window * 3))
        if len(history) < t.shape_min_points:
            return []
        series = (
            ("cpu_percent", tuple(s.cpu_percent for s in history)),
            ("ram_used_percent", tuple(s.ram_used_percent for s in history)),
        )
        return [
            self._shapes.find_weird(name, values, t.shape_window, t.shape_min_distance)
            for name, values in series
        ]
