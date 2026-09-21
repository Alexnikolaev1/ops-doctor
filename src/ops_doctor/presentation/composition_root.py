"""Composition root for Ops Doctor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ops_doctor.entities.host import GateThresholds
from ops_doctor.infrastructure.echo_shapes import EchoShapeAnalyzer
from ops_doctor.infrastructure.jsonl_store import JsonlSampleStore
from ops_doctor.infrastructure.psutil_sampler import PsutilHostSampler
from ops_doctor.use_cases.preflight import RecordAndPreflightUseCase


@dataclass(frozen=True, slots=True)
class Application:
    preflight: RecordAndPreflightUseCase
    store_path: Path


def default_store_path() -> Path:
    override = os.environ.get("OPS_DOCTOR_STORE")
    if override:
        return Path(override)
    return Path.home() / ".ops_doctor" / "samples.jsonl"


def build_application(
    store_path: Path | None = None, thresholds: GateThresholds | None = None
) -> Application:
    path = store_path or default_store_path()
    use_case = RecordAndPreflightUseCase(
        sampler=PsutilHostSampler(),
        store=JsonlSampleStore(path),
        shapes=EchoShapeAnalyzer(),
        thresholds=thresholds,
    )
    return Application(preflight=use_case, store_path=path)
