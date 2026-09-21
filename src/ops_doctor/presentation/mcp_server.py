"""Presentation layer: MCP server for Ops Doctor."""

from mcp.server.fastmcp import FastMCP

from ops_doctor.presentation.composition_root import build_application
from ops_doctor.presentation.formatting import format_preflight
from ops_doctor.use_cases.preflight import PreflightRequest

mcp = FastMCP("ops_doctor")
app = build_application()


@mcp.tool()
def host_preflight(heavy: bool = False) -> str:
    """Sample the Windows host now and decide if heavy agent work is safe.

    Hard BLOCK when free RAM/disk are too low or CPU is pegged.
    SOFT_WARN when CPU is elevated or Echo finds a strange recent shape
    in CPU/RAM history (sliding window). ALLOW otherwise.

    Args:
        heavy: Stricter thresholds for agency / compute_burst / nervous jobs.
    """
    report = app.preflight.execute(PreflightRequest(heavy=heavy))
    return format_preflight(report)


@mcp.tool()
def host_status() -> str:
    """Same as host_preflight(heavy=False) — quick pulse for the weak host."""
    return host_preflight(heavy=False)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
