"""Append-only JSONL sample store with bounded retention."""

from __future__ import annotations

import json
from pathlib import Path

from ops_doctor.entities.host import HostSample


class JsonlSampleStore:
    def __init__(self, path: Path, max_points: int = 288) -> None:
        self._path = path
        self._max_points = max_points
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("", encoding="utf-8")

    def append(self, sample: HostSample) -> None:
        rows = list(self._read_all())
        rows.append(sample)
        if len(rows) > self._max_points:
            rows = rows[-self._max_points :]
        self._write_all(rows)

    def recent(self, limit: int) -> tuple[HostSample, ...]:
        rows = self._read_all()
        if limit <= 0:
            return ()
        return tuple(rows[-limit:])

    def count(self) -> int:
        return len(self._read_all())

    def _read_all(self) -> list[HostSample]:
        text = self._path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        return [_from_dict(json.loads(line)) for line in text.splitlines()]

    def _write_all(self, rows: list[HostSample]) -> None:
        payload = "\n".join(json.dumps(_to_dict(row)) for row in rows)
        if payload:
            payload += "\n"
        self._path.write_text(payload, encoding="utf-8")


def _to_dict(sample: HostSample) -> dict[str, float]:
    return {
        "timestamp": sample.timestamp,
        "cpu_percent": sample.cpu_percent,
        "ram_used_percent": sample.ram_used_percent,
        "ram_available_mb": sample.ram_available_mb,
        "disk_free_gb": sample.disk_free_gb,
    }


def _from_dict(data: dict[str, float]) -> HostSample:
    return HostSample(
        timestamp=float(data["timestamp"]),
        cpu_percent=float(data["cpu_percent"]),
        ram_used_percent=float(data["ram_used_percent"]),
        ram_available_mb=float(data["ram_available_mb"]),
        disk_free_gb=float(data["disk_free_gb"]),
    )
