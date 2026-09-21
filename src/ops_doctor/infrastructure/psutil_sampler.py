"""Live host sampler via psutil."""

from __future__ import annotations

import os
import time
from pathlib import Path

import psutil  # type: ignore[import-untyped]

from ops_doctor.entities.host import HostSample


class PsutilHostSampler:
    def sample(self) -> HostSample:
        cpu = float(psutil.cpu_percent(interval=0.1))
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(_system_disk())
        return HostSample(
            timestamp=time.time(),
            cpu_percent=cpu,
            ram_used_percent=float(mem.percent),
            ram_available_mb=float(mem.available) / (1024 * 1024),
            disk_free_gb=float(disk.free) / (1024**3),
        )


def _system_disk() -> str:
    """Prefer the OS drive on Windows — cwd may live on a roomy data disk."""
    if os.name == "nt":
        windir = os.environ.get("SystemDrive", "C:")
        return windir + "\\"
    return Path.cwd().anchor or "/"
