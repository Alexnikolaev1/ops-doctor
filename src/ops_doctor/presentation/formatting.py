"""Human-readable preflight reports."""

from __future__ import annotations

from ops_doctor.entities.host import PreflightReport, ShapeFinding


def format_preflight(report: PreflightReport) -> str:
    sample = report.sample
    lines = [
        f"VERDICT: {report.verdict.value}",
        (
            f"Now: CPU {sample.cpu_percent:.0f}% | "
            f"RAM free {sample.ram_available_mb:.0f}MB "
            f"({sample.ram_used_percent:.0f}% used) | "
            f"Disk free {sample.disk_free_gb:.1f}GB"
        ),
        f"History points: {report.history_points}",
        _reasons_block(report.reasons),
    ]
    if report.shapes:
        lines.append("Shape scan:")
        lines.extend(_shape_line(shape) for shape in report.shapes)
    return "\n".join(lines)


def _reasons_block(reasons: tuple[str, ...]) -> str:
    if not reasons:
        return "Reasons: none — host looks fine for work"
    return "Reasons:\n" + "\n".join(f"  - {reason}" for reason in reasons)


def _shape_line(shape: ShapeFinding) -> str:
    flag = "WEIRD" if shape.weird else "ok"
    return f"  - {shape.metric}: {flag} (dist={shape.distance:.2f})"
