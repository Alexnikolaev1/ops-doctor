"""Ops Doctor tests: hard gates, soft shape, store, formatting."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ops_doctor.entities.host import GateThresholds, HostSample, Verdict
from ops_doctor.infrastructure.echo_shapes import EchoShapeAnalyzer
from ops_doctor.infrastructure.fakes import FakeSampler, FakeShapes, MemoryStore
from ops_doctor.infrastructure.jsonl_store import JsonlSampleStore
from ops_doctor.presentation.formatting import format_preflight
from ops_doctor.use_cases.preflight import PreflightRequest, RecordAndPreflightUseCase


def _ok() -> HostSample:
    return HostSample(1.0, 10.0, 40.0, 2048.0, 20.0)


def _uc(
    sample: HostSample,
    store: MemoryStore | None = None,
    shapes: FakeShapes | None = None,
    thresholds: GateThresholds | None = None,
) -> RecordAndPreflightUseCase:
    return RecordAndPreflightUseCase(
        FakeSampler(sample),
        store or MemoryStore(),
        shapes or FakeShapes(),
        thresholds,
    )


def test_block_when_ram_too_low():
    report = _uc(replace(_ok(), ram_available_mb=100.0)).execute(PreflightRequest())
    assert report.verdict is Verdict.BLOCK
    assert any("RAM" in r for r in report.reasons)


def test_block_when_disk_too_low():
    report = _uc(replace(_ok(), disk_free_gb=0.5)).execute(PreflightRequest())
    assert report.verdict is Verdict.BLOCK
    assert any("Disk" in r for r in report.reasons)


def test_block_when_cpu_pegged():
    report = _uc(replace(_ok(), cpu_percent=95.0)).execute(PreflightRequest())
    assert report.verdict is Verdict.BLOCK


def test_heavy_uses_stricter_ram_floor():
    report = _uc(replace(_ok(), ram_available_mb=600.0)).execute(
        PreflightRequest(heavy=True)
    )
    assert report.verdict is Verdict.BLOCK


def test_allow_when_host_healthy():
    report = _uc(_ok()).execute(PreflightRequest())
    assert report.verdict is Verdict.ALLOW
    assert report.history_points == 1


def test_soft_warn_on_elevated_cpu():
    report = _uc(replace(_ok(), cpu_percent=88.0)).execute(PreflightRequest())
    assert report.verdict is Verdict.SOFT_WARN
    assert any("elevated" in r for r in report.reasons)


def test_soft_warn_on_weird_shape():
    store = MemoryStore()
    store.seed([replace(_ok(), timestamp=float(i)) for i in range(40)])
    report = _uc(
        _ok(), store=store, shapes=FakeShapes(weird=True, distance=3.5)
    ).execute(PreflightRequest())
    assert report.verdict is Verdict.SOFT_WARN
    assert any("Strange" in r for r in report.reasons)


def test_jsonl_store_roundtrip(tmp_path: Path):
    path = tmp_path / "s.jsonl"
    store = JsonlSampleStore(path, max_points=3)
    for i in range(5):
        store.append(replace(_ok(), timestamp=float(i)))
    assert store.count() == 3
    assert store.recent(2)[-1].timestamp == 4.0


def test_echo_shape_marks_injected_spike():
    base = [10.0 + (i % 6) for i in range(48)]
    for i in range(12):
        base[30 + i] = 95.0 if i % 2 == 0 else 5.0
    finding = EchoShapeAnalyzer().find_weird("cpu_percent", tuple(base), 6, 1.5)
    assert finding.weird is True
    assert finding.distance >= 1.5


def test_format_preflight_includes_verdict():
    report = _uc(_ok()).execute(PreflightRequest())
    text = format_preflight(report)
    assert text.startswith("VERDICT: ALLOW")
    assert "CPU" in text


def test_format_includes_shape_scan_and_reasons():
    store = MemoryStore()
    store.seed([replace(_ok(), timestamp=float(i)) for i in range(40)])
    report = _uc(
        _ok(), store=store, shapes=FakeShapes(weird=True, distance=4.0)
    ).execute(PreflightRequest())
    text = format_preflight(report)
    assert "Shape scan:" in text
    assert "WEIRD" in text
    assert "Reasons:" in text


def test_echo_shape_handles_short_series():
    finding = EchoShapeAnalyzer().find_weird("cpu", (1.0, 2.0, 3.0), 6, 1.5)
    assert finding.weird is False
    assert "not enough" in finding.explanation


def test_jsonl_recent_zero_limit(tmp_path: Path):
    store = JsonlSampleStore(tmp_path / "s.jsonl")
    store.append(_ok())
    assert store.recent(0) == ()
